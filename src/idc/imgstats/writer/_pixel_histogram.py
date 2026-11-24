import argparse
import csv
import sys
from typing import List

from wai.logging import LOGGING_WARNING

from idc.api import ImageData, remove_alpha
from kasperl.api import make_list, StreamWriter
from seppl import MetaDataHandler
from seppl.variables import InputBasedVariableSupporter, variable_list


class PixelHistogramWriter(StreamWriter, InputBasedVariableSupporter):
    """
    Counts the pixels per label per image.
    """

    def __init__(self, output_file: str = None, normalized: bool = None, metadata_fields: List[str] = None,
                 omit_black: bool = None, omit_white: bool = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param output_file: the output file to save the pixel histogram to
        :type output_file: str
        :param normalized: whether to normalize the counts to 0-1
        :type normalized: boolean
        :param metadata_fields: the meta-data fields to add as columns as well
        :type metadata_fields: list
        :param omit_black: whether to omit the color black
        :type omit_black: bool
        :param omit_white: whether to omit the color white
        :type omit_white: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.output_file = output_file
        self.normalized = normalized
        self.metadata_fields = metadata_fields
        self.omit_black = omit_black
        self.omit_white = omit_white
        self._histograms = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pixel-histogram"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Generates a CSV file with the pixel histogram, one image per row."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output_file", type=str, help="The file to write the statistics to; uses stdout if omitted. " + variable_list(obj=self), required=False, default=None)
        parser.add_argument("-n", "--normalized", action="store_true", help="Whether to normalize the histograms to 0-1 range.")
        parser.add_argument("-m", "--metadata_fields", type=str, help="The additional meta-data fields to output.", required=False, default=None, nargs="*")
        parser.add_argument("-b", "--omit_black", action="store_true", help="Whether to skip the color black in the histogram.")
        parser.add_argument("-w", "--omit_white", action="store_true", help="Whether to skip the color white in the histogram.")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.output_file = ns.output_file
        self.normalized = ns.normalized
        self.metadata_fields = ns.metadata_fields
        self.omit_black = ns.omit_black
        self.omit_white = ns.omit_white

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageData]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.normalized is None:
            self.normalized = False
        if self.metadata_fields is None:
            self.metadata_fields = []
        if self.omit_black is None:
            self.omit_black = False
        if self.omit_white is None:
            self.omit_white = False
        self._histograms = None

    def output_csv(self):
        """
        Outputs the pixel histograms in CSV format.
        """
        if self.output_file is None:
            writer = csv.writer(sys.stdout)
            fp = None
        else:
            path = self.session.expand_variables(self.output_file)
            self.logger().info("Writing pixel histograms to: %s" % path)
            fp = open(path, "w")
            writer = csv.writer(fp)

        writer.writerows(self._histograms)

        if fp is not None:
            fp.close()

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        for item in make_list(data):
            row = [item.image_name]

            img = item.image
            if img.mode == 'RGBA':
                img = remove_alpha(img)
            channels = img.split()
            if (len(channels) == 3) or (len(channels) == 1):
                for channel in channels:
                    histo = channel.histogram()
                    if self.normalized:
                        normalized = [count / sum(histo) for count in histo]
                        histo = normalized
                    if self.omit_black:
                        histo = histo[1:]
                    if self.omit_white:
                        histo = histo[:-1]
                    row.extend(histo)
                meta = None
                if isinstance(item, MetaDataHandler):
                    meta = item.get_metadata()
                if meta is not None:
                    for field in self.metadata_fields:
                        if field in meta:
                            row.append(meta[field])
                        else:
                            row.append(None)
            else:
                self.logger().warning("Unhandled number of channels (accepted: 1 or 3): %d" % len(channels))
                continue

            # header?
            if self._histograms is None:
                self._histograms = []
                header = ["image"]
                if len(channels) == 3:
                    prefixes = ["red", "green", "blue"]
                else:
                    prefixes = ["gray"]
                for prefix in prefixes:
                    if self.omit_black:
                        start = 1
                    else:
                        start = 0
                    if self.omit_white:
                        stop = 255
                    else:
                        stop = 256
                    for i in range(start, stop):
                        header.append("%s-%d" % (prefix, i))
                for field in self.metadata_fields:
                    header.append(field)
                self._histograms.append(header)

            # data row
            self._histograms.append(row)

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.output_csv()
