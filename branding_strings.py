import os
import argparse
import glob

_NEW_BROWSER_NAME = "Ninja Browser"
_PATHS_TO_PATCH = [
	"chrome\\app\\theme\\chromium\\BRANDING",
	"chrome\\app\\generated_resources.grd",
	"chrome\\app\\chromium_strings.grd",
	"chrome\\app\\resources\\*.xtb"
]

def process(src_dir: str):
	strings_to_replace = [
		["org.chromium.Chromium", "org.ninja.browser"],
		["ChromiumOS", _NEW_BROWSER_NAME.replace(" ", "") + "OS"],
		["Chromium", _NEW_BROWSER_NAME],
		["Google Chrome", _NEW_BROWSER_NAME],
		["ChromeOS", _NEW_BROWSER_NAME.replace(" ", "") + "OS"],
		["Chrome", _NEW_BROWSER_NAME],
	]
	os.chdir(src_dir)
	for _path in _PATHS_TO_PATCH:
		for file_path in glob.glob(_path):
			with open(file_path, 'r', encoding='utf-8') as file:
				filedata = file.read()
			for pair in strings_to_replace:
				filedata = filedata.replace(pair[0], pair[1])
			with open(file_path, 'w', encoding='utf-8') as file:
				file.write(filedata)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--src', '-s', type=str, help='chromium "src" dir')

	args = parser.parse_args()
	process(args.src)
