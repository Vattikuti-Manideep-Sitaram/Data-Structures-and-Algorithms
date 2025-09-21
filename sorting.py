"""Classic sorting algorithms implemented for educational purposes."""
from __future__ import annotations
from typing import MutableSequence, TypeVar

T = TypeVar("T")


def selection_sort(values: MutableSequence[T]) -> MutableSequence[T]:
    """Sort ``values`` in-place using selection sort and return the sequence."""
    n = len(values)
    for i in range(n - 1):
        min_index = i
        for j in range(i + 1, n):
            if values[j] < values[min_index]:
                min_index = j
        if min_index != i:
            values[i], values[min_index] = values[min_index], values[i]
    return values


def bubble_sort(values: MutableSequence[T]) -> MutableSequence[T]:
    """Sort ``values`` in-place using bubble sort and return the sequence."""
    n = len(values)
    for end in range(n - 1, 0, -1):
        swapped = False
        for i in range(end):
            if values[i] > values[i + 1]:
                values[i], values[i + 1] = values[i + 1], values[i]
                swapped = True
        if not swapped:
            break
    return values


if __name__ == "__main__":
    samples = [
        [4, 3, 5, 6, 1],
        [4, 3, 2, 5, 1, 6, 23, 54, -1],
    ]
    print("Selection sort demo:")
    for sample in samples:
        print(selection_sort(sample.copy()))

    print("\nBubble sort demo:")
    for sample in samples:
        print(bubble_sort(sample.copy()))
