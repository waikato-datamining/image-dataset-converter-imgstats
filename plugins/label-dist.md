# label-dist

* accepts: idc.api.ImageClassificationData, idc.api.ObjectDetectionData, idc.api.ImageSegmentationData

Collects the labels and outputs their distribution.

```
usage: label-dist [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                  [-N LOGGER_NAME] [-o OUTPUT_FILE] [-f OUTPUT_FORMAT]
                  [-k LABEL_KEY] [-p]

Collects the labels and outputs their distribution.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        The file to write the statistics to; uses stdout if
                        omitted. Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
  -f OUTPUT_FORMAT, --output_format OUTPUT_FORMAT
                        The format to use for the output, available formats:
                        text, csv, json (default: text)
  -k LABEL_KEY, --label_key LABEL_KEY
                        The key in the (object detection) meta-data that
                        contains the label. (default: type)
  -p, --percentages     Whether to output percentages instead of counts.
                        (default: False)
```

Available placeholders:

* `{HOME}`: The home directory of the current user.
* `{CWD}`: The current working directory.
* `{TMP}`: The temp directory.
