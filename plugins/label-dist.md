# label-dist

* accepts: idc.api.ImageClassificationData, idc.api.ObjectDetectionData, idc.api.ImageSegmentationData

Collects the labels and outputs their distribution.

```
usage: label-dist [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                  [-N LOGGER_NAME] [--skip] [-o OUTPUT_FILE]
                  [-f {text,csv,json}] [-t {counts,percentages}]
                  [-k LABEL_KEY]

Collects the labels and outputs their distribution.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        The file to write the statistics to; uses stdout if
                        omitted. Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
  -f {text,csv,json}, --output_format {text,csv,json}
                        The format to use for the output. (default: text)
  -t {counts,percentages}, --output_type {counts,percentages}
                        How to output the distribution. (default: counts)
  -k LABEL_KEY, --label_key LABEL_KEY
                        The key in the (object detection) meta-data that
                        contains the label. (default: type)
```

Available placeholders:

* `{HOME}`: The home directory of the current user.
* `{CWD}`: The current working directory.
* `{TMP}`: The temp directory.
