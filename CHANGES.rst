Changelog
=========

0.1.1 (????-??-??)
------------------

- fixed handling of image classification data in `label-dist`, introduced the `-t/--output_type`
  output, which supersedes `-p/--percentages`


0.1.0 (2025-10-31)
------------------

- switched to `kasperl` library for base API and generic pipeline plugins
- added `pixel-count` writer that outputs pixel counts per label for image segmentation annotations
- added `contour-areas` writer that outputs size and location of contours in image and/or image segmentation annotations


0.0.2 (2025-03-14)
------------------

- switched to underscores in project name
- added support for placeholders: `area-histogram`, and `label-dist`


0.0.1 (2024-05-06)
------------------

- initial release

