# contour-areas

* accepts: idc.api.ImageClassificationData, idc.api.ObjectDetectionData, idc.api.ImageSegmentationData

Records the areas of contours of objects.

```
usage: contour-areas [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [-N LOGGER_NAME] [--skip] [-I {skip,fail}]
                     [-a {both,image,annotations}] [-m MIN_AREA] [-M MAX_AREA]
                     [-i] [-o OUTPUT_FILE] [-f OUTPUT_FORMAT]

Records the areas of contours of objects.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -I {skip,fail}, --incorrect_format_action {skip,fail}
                        The action to undertake if an invalid input format is
                        encountered. (default: skip)
  -a {both,image,annotations}, --apply_to {both,image,annotations}
                        Where to apply the filter to. (default: image)
  -m MIN_AREA, --min_area MIN_AREA
                        The minimum area for the contours in order to record
                        them. (default: None)
  -M MAX_AREA, --max_area MAX_AREA
                        The maximum area for the contours in order to record
                        them. (default: None)
  -i, --invert          Whether to invert the binary image, i.e., looking for
                        black specks rather than white ones. (default: False)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        The file to write the statistics to; uses stdout if
                        omitted. Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
  -f OUTPUT_FORMAT, --output_format OUTPUT_FORMAT
                        The format to use for the output, available formats:
                        csv, json (default: csv)
```

Available placeholders:

* `{HOME}`: The home directory of the current user.
* `{CWD}`: The current working directory.
* `{TMP}`: The temp directory.
