import argparse
import csv
import json
import statistics
import sys
from typing import List, Any, Dict

from wai.common.adams.imaging.locateobjects import LocatedObject
from wai.logging import LOGGING_WARNING

from idc.api import ObjectDetectionData, LABEL_KEY
from kasperl.api import make_list, StreamWriter
from seppl.variables import InputBasedVariableSupporter, variable_list

OUTPUT_FORMAT_TEXT = "text"
OUTPUT_FORMAT_CSV = "csv"
OUTPUT_FORMAT_JSON = "json"
OUTPUT_FORMATS = [
    OUTPUT_FORMAT_TEXT,
    OUTPUT_FORMAT_CSV,
    OUTPUT_FORMAT_JSON,
]

TARGET_BBOX_AREA = "bbox-area"
TARGET_POLYGON_AREA = "polygon-area"
TARGET_METADATA_VALUE = "meta-data-value"
TARGETS = [
    TARGET_BBOX_AREA,
    TARGET_POLYGON_AREA,
    TARGET_METADATA_VALUE,
]

CALCULATION_LIST = "list"
CALCULATION_COUNT = "count"
CALCULATION_SUM = "sum"
CALCULATION_MEAN = "mean"
CALCULATION_STDEV = "stdev"
CALCULATION_MIN = "min"
CALCULATION_MAX = "max"
CALCULATIONS = [
    CALCULATION_LIST,
    CALCULATION_COUNT,
    CALCULATION_SUM,
    CALCULATION_MIN,
    CALCULATION_MAX,
    CALCULATION_MEAN,
    CALCULATION_STDEV,
]


class ObjectCalculationsWriter(StreamWriter, InputBasedVariableSupporter):
    """
    Performs calculations on the object detection annotations.
    """

    def __init__(self, target: str = None, metadata_key: str = None, calculations: List[str] = None,
                 output_file: str = None, output_format: str = OUTPUT_FORMAT_TEXT,
                 labels: List[str] = None, per_image: bool = None, suppress_path: bool = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param target: what to use for the calculation
        :type target: str
        :param metadata_key: the key for the meta-data value to use
        :type metadata_key: str
        :param calculations: the type of calculation(s) to perform
        :type calculations: list
        :param output_file: the output file to save the label distribution to
        :type output_file: str
        :param output_format: the format for the output file
        :type output_format: str
        :param labels: the labels to record
        :type labels: list
        :param per_image: whether to output the statistics per image rather than for the complete run
        :type per_image: bool
        :param suppress_path: whether to suppress the path
        :type suppress_path: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
        self.metadata_key = metadata_key
        self.calculations = calculations
        self.output_file = output_file
        self.output_format = output_format
        self.labels = labels
        self.per_image = per_image
        self.suppress_path = suppress_path
        self._calculations = None
        self._labels = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "object-calculations"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Performs calculations on the object detection annotations."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-t", "--target", choices=TARGETS, help="What to use as basis for the calculations.", required=False, default=TARGET_BBOX_AREA)
        parser.add_argument("-k", "--metadata_key", type=str, help="The key of the object meta-data value to use.", required=False, default=None)
        parser.add_argument("-c", "--calculations", choices=CALCULATIONS, help="The type of calculation to apply to the targets.", required=False, default=[CALCULATION_COUNT], nargs="*")
        parser.add_argument("-o", "--output_file", type=str, help="The file to write the statistics to; uses stdout if omitted. " + variable_list(obj=self), required=False, default=None)
        parser.add_argument("-f", "--output_format", type=str, help="The format to use for the output, available formats: %s" % ", ".join(OUTPUT_FORMATS), required=False, default=OUTPUT_FORMAT_TEXT)
        parser.add_argument("--labels", type=str, help="The subset of labels to perform the calculations on rather than all.", required=False, default=None, nargs="*")
        parser.add_argument("--per_image", action="store_true", help="Whether to output the statistics per image rather than for the complete run.")
        parser.add_argument("--suppress_path", action="store_true", help="Whether to suppress the path in the output.")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.target = ns.target
        self.metadata_key = ns.metadata_key
        self.calculations = ns.calculations
        self.output_file = ns.output_file
        self.output_format = ns.output_format
        self.labels = ns.labels
        self.per_image = ns.per_image
        self.suppress_path = ns.suppress_path

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ObjectDetectionData]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.target is None:
            self.target = TARGET_BBOX_AREA
        if (self.target == TARGET_METADATA_VALUE) and (self.metadata_key is None):
            raise Exception("No meta-data key specified!")
        if self.calculations is None:
            self.calculations = [CALCULATION_COUNT]
        if (CALCULATION_LIST in self.calculations) and (len(self.calculations) > 1):
            raise Exception("When using '%s' as calculation, no other calculation is possible!" % CALCULATION_LIST)
        if self.output_format is None:
            self.output_format = OUTPUT_FORMAT_TEXT
        if self.per_image is None:
            self.per_image = False
        if self.suppress_path is None:
            self.suppress_path = False
        self._labels = set()
        if self.labels is not None:
            self._labels.update(self.labels)
        self._calculations = []

    def _get_stat_names(self):
        """
        Determines all the names of the values in the stats dictionaries, excluding 'name' and 'path'.

        :return: the sorted list of names
        :rtype: list
        """
        keys = set()
        for calculation in self._calculations:
            keys.update(calculation.keys())
        if "path" in keys:
            keys.remove("path")
        keys.remove("name")
        keys = sorted(list(keys))
        result = self.calculations[:]
        for key in keys:
            if key not in result:
                result.append(key)
        return result

    def output_text(self, use_stdout: bool):
        """
        Outputs the pixel counts in simple textual format.

        :param use_stdout: whether to use stdout or the file
        :type use_stdout: bool
        """
        if self.suppress_path:
            indent = ""
        else:
            indent = "  "
        keys = self._get_stat_names()
        if use_stdout:
            for calculation in self._calculations:
                if not self.suppress_path:
                    print("%s" % calculation["path"])
                print("%sname: %s" % (indent, calculation["name"]))
                for key in keys:
                    if key in calculation:
                        print("%s%s: %s" % (indent, key, str(calculation[key])))
                print()
        else:
            path = self.session.expand_variables(self.output_file)
            self.logger().info("Writing calculations to: %s" % path)
            with open(path, "w") as fp:
                for calculation in self._calculations:
                    if not self.suppress_path:
                        fp.write("%s\n" % calculation["path"])
                    fp.write("%sname: %s\n" % (indent, calculation["name"]))
                    for key in keys:
                        if key in calculation:
                            fp.write("%s%s: %s\n" % (indent, key, str(calculation[key])))
                    fp.write("\n")

    def output_csv(self, use_stdout: bool):
        """
        Outputs the pixel counts in CSV format.

        :param use_stdout: whether to use stdout or the file
        :type use_stdout: bool
        """
        if use_stdout:
            writer = csv.writer(sys.stdout)
            fp = None
        else:
            path = self.session.expand_variables(self.output_file)
            self.logger().info("Writing calculations to: %s" % path)
            fp = open(path, "w")
            writer = csv.writer(fp)

        # header
        keys = self._get_stat_names()
        row = []
        if not self.suppress_path:
            row.append("path")
        row.append("name")
        row.extend(keys)
        writer.writerow(row)

        # data
        for calculation in self._calculations:
            row = []
            if not self.suppress_path:
                row.append(calculation["path"])
            row.append(calculation["name"])
            for key in keys:
                if key in calculation:
                    row.append(calculation[key])
                else:
                    row.append(None)
            writer.writerow(row)

        if fp is not None:
            fp.close()

    def output_json(self, use_stdout: bool):
        """
        Outputs the pixel counts in json format.

        :param use_stdout: whether to use stdout or the file
        :type use_stdout: bool
        """
        if use_stdout:
            print(json.dumps(self._calculations, indent=2))
        else:
            path = self.session.expand_variables(self.output_file)
            self.logger().info("Writing calculations to: %s" % path)
            with open(path, "w") as fp:
                json.dump(self._calculations, fp, indent=2)

    def output_calculations(self):
        """
        Outputs the distribution.
        """
        use_stdout = (self.output_file is None) or (len(self.output_file) == 0)

        if self.output_format == OUTPUT_FORMAT_TEXT:
            self.output_text(use_stdout)
        elif self.output_format == OUTPUT_FORMAT_CSV:
            self.output_csv(use_stdout)
        elif self.output_format == OUTPUT_FORMAT_JSON:
            self.output_json(use_stdout)
        else:
            raise Exception("Unhandled output format: %s" % self.output_format)

    def _get_value(self, obj: LocatedObject):
        """
        Extracts the relevant value from the object.

        :param obj: the object to process
        :type obj: LocatedObject
        :return: the value, None if failed to extract
        """
        # check label?
        if len(self._labels) > 0:
            if LABEL_KEY in obj.metadata:
                if obj.metadata[LABEL_KEY] not in self._labels:
                    return None
            else:
                return None

        if self.target == TARGET_BBOX_AREA:
            return obj.width * obj.height
        elif self.target == TARGET_POLYGON_AREA:
            if obj.has_polygon():
                return obj.get_polygon().area()
        elif self.target == TARGET_METADATA_VALUE:
            if self.metadata_key in obj.metadata:
                return obj.metadata[self.metadata_key]
        else:
            raise Exception("Unhandled target: %s" % self.target)
        return None

    def _calculate(self, values: List[Any]) -> List[Dict[str, Any]]:
        """
        Performs the calculations.

        :param values: the values to use as basis
        :type values: list
        :return: the calculated value(s), one calculation dict per list entry
        :rtype: list
        """
        result = []
        if CALCULATION_LIST in self.calculations:
            if self.target == TARGET_METADATA_VALUE:
                name = self.metadata_key
            else:
                name = self.target
            for value in values:
                result.append({name: value})
        else:
            result_calc = dict()
            result.append(result_calc)
            for calculation in self.calculations:
                result_calc[calculation] = result_calc
                if calculation == CALCULATION_COUNT:
                    result_calc[calculation] = len(values)
                elif calculation == CALCULATION_MIN:
                    if len(values) > 0:
                        result_calc[calculation] = min(values)
                elif calculation == CALCULATION_MAX:
                    if len(values) > 0:
                        result_calc[calculation] = max(values)
                elif calculation == CALCULATION_SUM:
                    if len(values) > 0:
                        result_calc[calculation] = sum(values)
                elif calculation == CALCULATION_MEAN:
                    if (len(values)) > 0:
                        result_calc[calculation] = statistics.mean(values)
                elif calculation == CALCULATION_STDEV:
                    if (len(values)) > 0:
                        result_calc[calculation] = statistics.stdev(values)
                else:
                    raise Exception("Unhandled calculation: %s" % calculation)
        return result

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        for item in make_list(data):
            # determine objects
            objs = []
            if item.has_annotation():
                if len(self._labels) > 0:
                    objs = []
                    ann = item.get_absolute()
                    for obj in ann:
                        if (LABEL_KEY in obj.metadata) and (obj.metadata[LABEL_KEY] in self._labels):
                            objs.append(obj)
                else:
                    objs = item.get_absolute()

            # extract values
            values = []
            for obj in objs:
                value = self._get_value(obj)
                if value is not None:
                    values.append(value)

            # calculate
            values_calc = self._calculate(values)

            # append stats
            stats = dict()
            if not self.suppress_path:
                stats["path"] = item.source
            stats["name"] = item.image_name
            if len(self._labels) > 0:
                stats["labels"] = ",".join(self.labels)
            for value in values_calc:
                curr = stats.copy()
                curr.update(value)
                self._calculations.append(curr)

            if self.per_image:
                self.output_calculations()
                self._calculations = []

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        if not self.per_image:
            self.output_calculations()
