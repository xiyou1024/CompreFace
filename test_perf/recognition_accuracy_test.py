import argparse

import imageio
from sklearn.datasets import fetch_lfw_people

from main import ROOT_DIR
from src.init_runtime import init_runtime
from test_perf._data_wrangling import split_train_test, parse_lfw_data
from test_perf._model_wrappers import EfrsLocal, ModelWrapperBase, EfrsRestApi
from test_perf.dto import Dataset

IMG_DIR = ROOT_DIR / 'test_files'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host')
    parser.add_argument('--test', action='store_true')
    return parser.parse_args()


def get_lfw_dataset() -> Dataset:
    lfw_data = fetch_lfw_people(min_faces_per_person=2, color=True, funneled=False)
    dataset_full = parse_lfw_data(lfw_data)
    return split_train_test(dataset_full)


def get_test_dataset() -> Dataset:
    dataset_full = [
        ('Person A', imageio.imread(IMG_DIR / 'personA-img1.jpg')),
        ('Person A', imageio.imread(IMG_DIR / 'personA-img2.jpg')),
        ('Person B', imageio.imread(IMG_DIR / 'personB-img1.jpg'))
    ]
    return split_train_test(dataset_full)


def calculate_accuracy(model: ModelWrapperBase, dataset: Dataset) -> float:
    for name, img in dataset.train:
        model.add_face_example(img, name)
    model.train()
    return sum(name == model.recognize(img) for name, img in dataset.test) / len(dataset.test)


if __name__ == '__main__':
    init_runtime()
    args = parse_args()
    model = EfrsRestApi(args.host) if args.host else EfrsLocal()
    dataset = get_test_dataset() if args.test else get_lfw_dataset()

    accuracy = calculate_accuracy(model, dataset)

    print(f'Accuracy: {accuracy * 100}%\nTraining set size: {len(dataset.train)}\nTest set size: {len(dataset.test)}')
