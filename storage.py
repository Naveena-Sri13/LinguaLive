import os
import json

from config import DATA_DIR


def ensure_data_folder():

    if not os.path.exists(
        DATA_DIR
    ):

        os.makedirs(
            DATA_DIR
        )


def load_json_file(
    file_path,
    default_value
):

    try:

        ensure_data_folder()

        if os.path.exists(
            file_path
        ):

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(
                    file
                )

        return default_value

    except Exception:

        return default_value


def save_json_file(
    file_path,
    data
):

    ensure_data_folder()

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )