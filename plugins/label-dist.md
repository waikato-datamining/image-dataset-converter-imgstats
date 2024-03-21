# label-dist

* accepts: idc.api.ImageClassificationData, idc.api.ObjectDetectionData, idc.api.ImageSegmentationData

Collects the labels and outputs their distribution.

```
usage: label-dist [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                  [-N LOGGER_NAME] [-r SPLIT_RATIOS [SPLIT_RATIOS ...]]
                  [-n SPLIT_NAMES [SPLIT_NAMES ...]] [-o OUTPUT_FILE]
                  [-f OUTPUT_FORMAT] [-k LABEL_KEY] [-p]

Collects the labels and outputs their distribution.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -r SPLIT_RATIOS [SPLIT_RATIOS ...], --split_ratios SPLIT_RATIOS [SPLIT_RATIOS ...]
                        The split ratios to use for generating the splits
                        (must sum up to 100) (default: None)
  -n SPLIT_NAMES [SPLIT_NAMES ...], --split_names SPLIT_NAMES [SPLIT_NAMES ...]
                        The split names to use for the generated splits.
                        (default: None)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        The file to write the statistics to; uses stdout if
                        omitted. (default: None)
  -f OUTPUT_FORMAT, --output_format OUTPUT_FORMAT
                        The format to use for the output, available modes:
                        csv, json (default: text)
  -k LABEL_KEY, --label_key LABEL_KEY
                        The key in the (object detection) meta-data that
                        contains the label. (default: type)
  -p, --percentages     Whether to output percentages instead of counts.
                        (default: False)
```
