# SPDX-License-Identifier: MIT
import pathlib, tempfile, subprocess, os.path

from .core import FWPackage
from .wifi import WiFiFWCollection
from .bluetooth import BluetoothFWCollection
from .multitouch import MultitouchFWCollection
from .kernel import KernelFWCollection

def update_firmware(source, dest):
    raw_fw = source.joinpath("all_firmware.tar.gz")
    if not raw_fw.exists():
        print(f"Could not find {raw_fw}")
    
    pkg = FWPackage(os.path.join(dest, "firmware.tar"),
                    os.path.join(dest, "firmware.cpio"))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        subprocess.run(["tar", "xf", str(raw_fw.resolve())], cwd=tmpdir, check=True)

        col = WiFiFWCollection(str(tmpdir.joinpath("firmware", "wifi")))
        pkg.add_files(sorted(col.files()))

        col = BluetoothFWCollection(str(tmpdir.joinpath("firmware", "bluetooth")))
        pkg.add_files(sorted(col.files()))

        col = MultitouchFWCollection(str(tmpdir.joinpath("fud_firmware")))
        pkg.add_files(sorted(col.files()))

    col = KernelFWCollection(str(source))
    pkg.add_files(sorted(col.files()))

    pkg.close()

    pkg.save_manifest(os.path.join(dest, "manifest.txt"))

def main():
    import argparse
    import logging
    logging.basicConfig()

    parser = argparse.ArgumentParser(description='Update vendor firmware tarball')
    parser.add_argument('source', metavar='SOURCE', type=pathlib.Path,
                        help='path containing raw firmware')
    parser.add_argument('dest', metavar='DEST', type=pathlib.Path,
                        help='output path for vendor firmware')
    
    args = parser.parse_args()

    update_firmware(args.source, args.dest)

if __name__ == "__main__":
    main()
