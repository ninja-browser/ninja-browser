# ninja-browser

Based on ungoogled-chromium project browser with integrated extensions for ad-blocking, advanced privacy protection, and easy downloads of videos, music, and images

## Downloads

[Download bins page](https://ninja-browser.github.io/ninja-browser/).

## Building

* follow instructions from [googled-chromium-window](https://github.com/ungoogled-software/ungoogled-chromium-windows) project to setting up the build environment and build base Chromium
* run: `{git folder}\usr\bin\patch.exe branding_executable.patch`
* run: `python3 branding_strings.py`
* run: `python3 prepare_extensions.py`
* rebuild chromium (`ungoogled-chromium-windows\build\src>ninja -C out\Default chrome mini_installer`)


## License

BSD-3-clause. See [LICENSE](LICENSE)