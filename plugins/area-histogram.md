# area-histogram

* accepts: idc.api.ObjectDetectionData, idc.api.ImageSegmentationData

Generates histograms of the area (normalized or absolute) occupied by the annotations.

```
usage: area-histogram [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                      [-N LOGGER_NAME] [--skip] [-o OUTPUT_FILE]
                      [-f OUTPUT_FORMAT] [-k LABEL_KEY] [-B NUM_BINS] [-b]
                      [-n] [-a LABEL]

Generates histograms of the area (normalized or absolute) occupied by the
annotations.

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
                        omitted. Supported placeholders: {HOME}, {CWD}, {TMP},
                        {INPUT_PATH}, {INPUT_NAMEEXT}, {INPUT_NAMENOEXT},
                        {INPUT_EXT}, {INPUT_PARENT_PATH}, {INPUT_PARENT_NAME}
                        (default: None)
  -f OUTPUT_FORMAT, --output_format OUTPUT_FORMAT
                        The format to use for the output, available formats:
                        text, csv, json (default: text)
  -k LABEL_KEY, --label_key LABEL_KEY
                        The key in the (object detection) meta-data that
                        contains the label. (default: type)
  -B NUM_BINS, --num_bins NUM_BINS
                        The number of bins to use for the histogram. (default:
                        20)
  -b, --force_bbox      Whether to use the bounding box even if a polygon is
                        present (object detection domain only) (default:
                        False)
  -n, --normalized      Whether to use normalized areas (using the image size
                        as base) (default: False)
  -a LABEL, --all_label LABEL
                        The label to use for all the labels combined.
                        (default: ALL)
```

Available placeholders:

* `{HOME}`: The home directory of the current user.
* `{CWD}`: The current working directory.
* `{TMP}`: The temp directory.
* `{INPUT_PATH}`: The directory part of the current input, i.e., `/some/where` of input `/some/where/file.txt`.
* `{INPUT_NAMEEXT}`: The name (incl extension) of the current input, i.e., `file.txt` of input `/some/where/file.txt`.
* `{INPUT_NAMENOEXT}`: The name (excl extension) of the current input, i.e., `file` of input `/some/where/file.txt`.
* `{INPUT_EXT}`: The extension of the current input (incl dot), i.e., `.txt` of input `/some/where/file.txt`.
* `{INPUT_PARENT_PATH}`: The directory part of the parent directory of the current input, i.e., `/some` of input `/some/where/file.txt`.
* `{INPUT_PARENT_NAME}`: The name of the parent directory of the current input, i.e., `where` of input `/some/where/file.txt`.
