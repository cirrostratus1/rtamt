from rtamt.operation.abstract_operation import AbstractOperation
from rtamt.operation.sample import Sample
from rtamt.operation.sample import Time

class DivisionOperation(AbstractOperation):
    def __init__(self):
        self.input = []

    def addNewInput(self, left, right):
        sample = Sample()
        self.input.append(sample)
        self.input[0].time = Time()
        sample = Sample()
        self.input.append(sample)
        self.input[1].time = Time()

        self.input[0].seq = left.seq
        self.input[0].time.sec = left.time.sec
        self.input[0].time.msec = left.time.msec
        self.input[0].value = left.value

        self.input[1].seq = right.seq
        self.input[1].time.sec = right.time.sec
        self.input[1].time.msec = right.time.msec
        self.input[1].value = right.value

    def update(self):
        out = Sample()
        val = self.input[0].value / self.input[1].value

        out.seq = self.input[0].seq
        out.value = val

        return out