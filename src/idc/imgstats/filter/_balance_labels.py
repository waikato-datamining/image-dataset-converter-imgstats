import argparse
import json
from random import Random
from typing import List

from wai.logging import LOGGING_WARNING

from idc.api import ImageClassificationData
from kasperl.api import make_list, flatten_list
from seppl.io import Filter


class BalanceImageClassificationLabels(Filter):
    """
    Tries to balance labels in an image stream by dropping images that don't make the threshold.
    Loads the correction from a JSON file, a probability of 0-1 per label.
    Assumes no correction necessary if label not present in correction file.
    """

    def __init__(self, label_correction: str = None, seed: int = None, default_probability: float = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param label_correction: the JSON file with the label balance correction (probability 0-1 per label)
        :type label_correction: str
        :param seed: the seed value to use for the random number generator; randomly seeded if not provided
        :type seed: int
        :param default_probability: the default to use as probability if a label is not present (0: discard, 1: keep)
        :type default_probability: float
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.label_correction = label_correction
        self.seed = seed
        self.default_probability = default_probability
        self._correction = None
        self._random = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "balance-labels-ic"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Tries to balance labels in an image stream by dropping images that don't make the threshold. Loads the correction from a JSON file, a probability of 0-1 per label. Assumes no correction necessary if label not present in correction file. Such a correction file for a balanced label distribution can be generated automatically using 'label-dist'."

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageClassificationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ImageClassificationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-c", "--label_correction", type=str, help="The JSON file with the probabilities per label.", required=False, default=None)
        parser.add_argument("-s", "--seed", type=int, help="The seed value to use for the random number generator; randomly seeded if not provided", default=None, required=False)
        parser.add_argument("-p", "--default_probability", type=float, help="The default probability [0-1] to use if a label is not mentioned in the correction file: 0=discard, 1=keep", default=1.0, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.label_correction = ns.label_correction
        self.seed = ns.seed
        self.default_probability = ns.default_probability

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._random = Random(self.seed)
        if self.default_probability is None:
            self.default_probability = 1.0
        if self.label_correction is None:
            self.logger().warning("No JSON file with label corrections provided, no correction possible!")
        else:
            self._correction = dict()
            path = self.session.expand_placeholders(self.label_correction)
            self.logger().info("Loading correction file: %s" % path)
            with open(path, "r") as fp:
                probs = json.load(fp)
                for k in probs:
                    try:
                        prob = float(probs[k])
                        self._correction[k] = prob
                    except:
                        self.logger().warning("Failed to parse probability for %s: %s" % (str(k), str(probs[k])))
            self.logger().info("Correction: %s" % str(self._correction))

    def _do_process(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        result = []
        for item in make_list(data):
            add = False
            if isinstance(item, ImageClassificationData):
                if item.has_annotation():
                    prob = self.default_probability
                    label = item.annotation
                    if label in self._correction:
                        prob = self._correction[label]
                    if self._random.random() < prob:
                        add = True
                else:
                    self.logger().warning("Skipping, due to no label: " + str(item))
            else:
                self.logger().warning("Skipping due to wrong data type: %s" % str(type(item)))
            if add:
                result.append(item)

        return flatten_list(result)
