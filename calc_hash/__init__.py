import hashlib

from fman import DirectoryPaneCommand, show_alert, show_prompt, clipboard
from fman.fs import is_dir
from fman.url import as_human_readable

hash_map = {
    method: getattr(hashlib, method) for method in hashlib.hashlib.algorithms_guaranteed
}


class CalcHash(DirectoryPaneCommand):
    def __call__(self):
        valid_methods = ", ".join(hash_map.keys())
        chosen_files = self.get_chosen_files()
        results = []
        if chosen_files:
            hmeth, okay = show_prompt(
                f"Enter one of the following hashing methods: {valid_methods}"
            )
            hmeth = hmeth.strip()
            if hmeth not in hash_map.keys():
                response = show_alert("Invalid hash method.")
                break
            if okay:
                for fl in chosen_files:
                    if not is_dir(fl):
                        fhash = file_hash(fl, hmeth)
                        hstr = f"{as_human_readable(fl)}: {fhash}"
                        results.append(hstr)
                print(results)
                all_results = "\n".join(results)
                clipboard.set_text(all_results)
                response = show_alert(
                    "File hash(es) have been copied to your clipboard."
                )
            else:
                show_alert("No action taken.")


def file_hash(filename, method="sha1"):
    hashfunc = hash_map[method]
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hashfunc.update(chunk)
    return hashfunc.digest()
