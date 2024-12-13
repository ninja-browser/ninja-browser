import os
import shutil
import argparse
import json
from crx3 import creator
from crx3 import verifier

parser = argparse.ArgumentParser()
parser.add_argument('--src', '-s', type=str, help='chromium "src" dir')

args = parser.parse_args()

work_dir = os.path.dirname(os.path.realpath(__file__))
source_extensions_dir = os.path.join(work_dir, "extensions")
output_root_dir = args.src if args.src else os.path.join(work_dir, "src_for_replace")
output_crx_dir = os.path.join(output_root_dir, "chrome", "browser", "extensions", "default_extensions")

build_gn_file = os.path.join(output_crx_dir, "BUILD.gn")
our_extension_cc_file = os.path.join(output_root_dir, "extensions", "common", "our_extension.cc")

EXTENSIONS_TO_DELETE = []

def build_our_extension_cc_file(extensions_info):
	template = '\
#include "extensions/common/extension.h"\n\
namespace extensions {\n\
	const int kOurNumExtensions = __REPLACE_1__;\n\
	const OurExtension kOurExtensions[kOurNumExtensions] = {\n\
	/*{\n\
		char id[33];\n\
		char version[17];\n\
		char filename[255];\n\
	}*/\n\
__REPLACE_2__\n\
	};\n\
\n\
	const int kOurNumDeleteExtensions = __REPLACE_3__;\n\
	const char* kOurDeleteExtensions[kOurNumDeleteExtensions] = {\n\
		__REPLACE_4__\n\
	};\n\
}   // namespace extensions\n'

	template = template\
					.replace('__REPLACE_1__', str(len(extensions_info)))\
						.replace('__REPLACE_2__', ',\n'.join(['{{ "{}","{}","{}" }}'.format(ext['id'], ext['version'], ext['filename']) for ext in extensions_info]))\
					.replace('__REPLACE_3__', str(len(EXTENSIONS_TO_DELETE)))\
						.replace('__REPLACE_4__', ',\n'.join(['"{}"'.format(ext) for ext in EXTENSIONS_TO_DELETE]))
	with open(our_extension_cc_file, "w", encoding='utf-8') as cc_file:
		cc_file.write(template)

def build_build_gn_file(extensions_info):
	template = '\
if (is_win) {\n\
  copy("default_extensions") {\n\
    sources = [ \n\
      "external_extensions.json", \n\
__REPLACE__\n\
    ]\n\
    outputs = [ "$root_out_dir/extensions/{{source_file_part}}" ]\n\
  }\n\
} else {\n\
  group("default_extensions") {}\n\
}\n'

	template = template.replace('__REPLACE__', ',\n'.join(['"{}"'.format(ext['filename']) for ext in extensions_info]))
	with open(build_gn_file, "w", encoding='utf-8') as cc_file:
		cc_file.write(template)

def process():
	extensions_info = []

	files = os.listdir(output_crx_dir)
	for file in files:
		file_path = os.path.join(output_crx_dir, file)
		if os.path.isfile(file_path) and file.endswith(".crx"):
			os.remove(file_path)

	extensions = os.listdir(source_extensions_dir)
	for extension in extensions:
		extension_source = os.path.join(source_extensions_dir, extension, "source")
		manifest_file = os.path.join(extension_source, "manifest.json")
		pem_file = os.path.join(source_extensions_dir, extension, "key.pem")
		extension_output_crx = os.path.join(output_crx_dir, extension + ".crx")
		if os.path.isdir(extension_source):
			if not os.path.exists(pem_file):
				print("WARNING!!! key.pem for '" + extension + "' not exists, new key.pem will be generated")
				creator.create_private_key_file(pem_file)
			with open(manifest_file, "r", encoding='utf-8') as m_file:
				manifest = json.loads(m_file.read())
			creator.create_crx_file(extension_source, pem_file, extension_output_crx)
			verifier_result, header_info = verifier.verify(extension_output_crx)
			extensions_info.append({
				"id": header_info.crx_id,
				"version": manifest["version"],
				"filename": extension + ".crx",
			})

	build_our_extension_cc_file(extensions_info)
	build_build_gn_file(extensions_info)


if __name__ == '__main__':
	process()
