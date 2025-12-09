# balance-labels-ic

* accepts: idc.api.ImageClassificationData
* generates: idc.api.ImageClassificationData

Tries to balance labels in an image stream by dropping images that don't make the threshold. Loads the correction from a JSON file, a probability of 0-1 per label. Assumes no correction necessary if label not present in correction file. Such a correction file for a balanced label distribution can be generated automatically using 'label-dist'.

```
usage: balance-labels-ic [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         [-N LOGGER_NAME] [--skip] [-c LABEL_CORRECTION]
                         [-s SEED] [-p DEFAULT_PROBABILITY]

Tries to balance labels in an image stream by dropping images that don't make
the threshold. Loads the correction from a JSON file, a probability of 0-1 per
label. Assumes no correction necessary if label not present in correction
file. Such a correction file for a balanced label distribution can be
generated automatically using 'label-dist'.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -c LABEL_CORRECTION, --label_correction LABEL_CORRECTION
                        The JSON file with the probabilities per label.
                        (default: None)
  -s SEED, --seed SEED  The seed value to use for the random number generator;
                        randomly seeded if not provided (default: None)
  -p DEFAULT_PROBABILITY, --default_probability DEFAULT_PROBABILITY
                        The default probability [0-1] to use if a label is not
                        mentioned in the correction file: 0=discard, 1=keep
                        (default: 1.0)
```
