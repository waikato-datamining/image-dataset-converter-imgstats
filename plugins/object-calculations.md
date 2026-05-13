# object-calculations

* accepts: idc.api.ObjectDetectionData

Performs calculations on the object detection annotations.

```
usage: object-calculations [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                           [-N LOGGER_NAME] [--skip]
                           [-t {bbox-area,polygon-area,meta-data-value}]
                           [-k METADATA_KEY]
                           [-c [{list,count,sum,min,max,mean,stdev} ...]]
                           [-o OUTPUT_FILE] [-f OUTPUT_FORMAT]
                           [--labels [LABELS ...]] [--per_image]
                           [--suppress_path]

Performs calculations on the object detection annotations.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -t {bbox-area,polygon-area,meta-data-value}, --target {bbox-area,polygon-area,meta-data-value}
                        What to use as basis for the calculations. (default:
                        bbox-area)
  -k METADATA_KEY, --metadata_key METADATA_KEY
                        The key of the object meta-data value to use.
                        (default: None)
  -c [{list,count,sum,min,max,mean,stdev} ...], --calculations [{list,count,sum,min,max,mean,stdev} ...]
                        The type of calculation to apply to the targets.
                        (default: ['count'])
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        The file to write the statistics to; uses stdout if
                        omitted. Supported variables: {HOME}, {CWD}, {TMP},
                        {INPUT_PATH}, {INPUT_NAMEEXT}, {INPUT_NAMENOEXT},
                        {INPUT_EXT}, {INPUT_PARENT_PATH}, {INPUT_PARENT_NAME}
                        (default: None)
  -f OUTPUT_FORMAT, --output_format OUTPUT_FORMAT
                        The format to use for the output, available formats:
                        text, csv, json (default: text)
  --labels [LABELS ...]
                        The subset of labels to perform the calculations on
                        rather than all. (default: None)
  --per_image           Whether to output the statistics per image rather than
                        for the complete run. (default: False)
  --suppress_path       Whether to suppress the path in the output. (default:
                        False)
```

Available variables:

* `{HOME}`: The home directory of the current user.
* `{CWD}`: The current working directory.
* `{TMP}`: The temp directory.
* `{INPUT_PATH}`: The directory part of the current input, i.e., `/some/where` of input `/some/where/file.txt`.
* `{INPUT_NAMEEXT}`: The name (incl extension) of the current input, i.e., `file.txt` of input `/some/where/file.txt`.
* `{INPUT_NAMENOEXT}`: The name (excl extension) of the current input, i.e., `file` of input `/some/where/file.txt`.
* `{INPUT_EXT}`: The extension of the current input (incl dot), i.e., `.txt` of input `/some/where/file.txt`.
* `{INPUT_PARENT_PATH}`: The directory part of the parent directory of the current input, i.e., `/some` of input `/some/where/file.txt`.
* `{INPUT_PARENT_NAME}`: The name of the parent directory of the current input, i.e., `where` of input `/some/where/file.txt`.
