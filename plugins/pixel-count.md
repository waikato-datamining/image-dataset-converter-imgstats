# pixel-count

* accepts: idc.api.ImageSegmentationData

Counts the pixels per label per image.

```
usage: pixel-count [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [--skip] [-o OUTPUT_FILE]
                   [-f OUTPUT_FORMAT] --labels LABELS [LABELS ...]
                   [--per_image] [--suppress_path]

Counts the pixels per label per image.

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
  -f OUTPUT_FORMAT, --output_format OUTPUT_FORMAT
                        The format to use for the output, available formats:
                        text, csv, json (default: text)
  --labels LABELS [LABELS ...]
                        The labels to calculate the pixel count for. (default:
                        None)
  --per_image           Whether to output the statistics per image rather than
                        for the complete run. (default: False)
  --suppress_path       Whether to suppress the path in the output. (default:
                        False)
```

Available placeholders:

* `{HOME}`: The home directory of the current user.
* `{CWD}`: The current working directory.
* `{TMP}`: The temp directory.
