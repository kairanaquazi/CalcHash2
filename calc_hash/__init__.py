import hashlib

from fman import DirectoryPaneCommand, show_alert, show_prompt, clipboard
from fman.fs import is_dir
from fman.url import as_human_readable

hash_map = {
    method: getattr(hashlib, method) for method in hashlib.algorithms_guaranteed
}


class CalcHash(DirectoryPaneCommand):
    def __call__(self):
        valid_methods = "\n".join(f" - {hm}" for hm in hash_map.keys())
        chosen_files = self.get_chosen_files()
        results = []

        # perform some checks on the selected files
        # as of now, only individual files are allowed, not directories
        dirs_in_selection = any([is_dir(fl) for fl in chosen_files])
        if dirs_in_selection:
            show_alert("Please specify individual files, not directories.")
            return
        else:
            hmeth, okay = show_prompt(
                f"Enter one of the following hashing methods:\n{valid_methods}"
            )
            hmeth = hmeth.strip()
            if hmeth not in hash_map.keys():
                response = show_alert("Invalid hashing method. No action taken.")
                return
        s = None
        if hmeth in ["shake_128", "shake_256"]:
            s, okay = show_prompt(
                "Enter the size of the hash:"
            )
            if not s.isnumeric():
                response = show_alert("Invalid integer. Goodbye!")
                return
            s = int(s)

        # perform the actual hash calculations
        num_selected_files = len(chosen_files)
        for fl in chosen_files:
            fl = as_human_readable(fl)
            fhash = file_hash(fl, hmeth, s)
            hstr = f"{fl}: {fhash}"
            results.append(hstr)
            all_results = "\n".join(results)
            clipboard.set_text(all_results)
        if num_selected_files == 1:
            msg = (
                f"The path and {hmeth} hash of the specified file has been copied to your clipboard."
            )
        else:
            msg = f"The paths and {hmeth} hashes of the {num_selected_files} selected files have been copied to your clipboard."
        response = show_alert(msg)


def file_hash(filename, method="sha1", s=None):
    hashfunc = hash_map[method]()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hashfunc.update(chunk)
    if s is not None:
        return hashfunc.hexdigest()
    return hashfunc.hexdigest(s)
