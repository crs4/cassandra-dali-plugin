# Copyright 2022 CRS4 (http://www.crs4.it/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from crs4.cassandra_utils._cassandra_session import CassandraSession
import pandas as pd
import numpy as np
import pickle


class split_generator:
    def __init__(self, data_id_col=None, metadata_id_col=None, data_col=None, data_label_col=None, metadata_label_col=None, label_type=None):
        ## Preliminary check on arguments
        if label_type != "none" and not metadata_label_col:
            raise Exception("Please provide the label_col argument")

        self._df = None
        self._metadata_id_col = metadata_id_col
        if data_id_col: 
            self._data_id_col = data_id_col
        else:
            self._data_id_col = metadata_id_col

        self._metadata_label_col = metadata_label_col
        if data_label_col:
            self._data_label_col = data_label_col
        else:
            self._data_label_col = metadata_label_col

        self._label_type = label_type
        
        self._data_col = data_col
        self._data_table = None
        self._metadata_table = None

    def load_from_db(self, cass_conf, data_table, metadata_table):
        self._data_table = data_table
        self._metadata_table = metadata_table
        self.cass_conf = cass_conf
        self._df = self.get_df_from_metadata()
        self.setup()

    def load_from_file(self, fn):
        dict_tmp = pickle.load(open(fn, "rb"))
        self._data_table = dict_tmp["data_table"]
        self._metadata_table = dict_tmp["metadata_table"]
        self._df = dict_tmp["df"]
        self.setup()

    def cache_db_data_to_file(self, fn):
        if (
            not isinstance(self._df, pd.DataFrame)
            or not self._data_table
            or not self._metadata_table
        ):
            raise Exception("No dataframe defined yet.")
        dict_tmp = {
            "data_table": self._data_table,
            "metadata_table": self._metadata_table,
            "df": self._df,
        }

        pickle.dump(dict_tmp, open(fn, "wb"))

    def setup(self):
        self.split_metadata = {
            "data_table": self._data_table,
            "data_id_col": self._data_id_col,
            "data_label_col": self._data_label_col,
            "metadata_table": self._metadata_table,
            "medadata_id_col": self._metadata_id_col,
            "metadata_label_col": self._metadata_label_col,
            "data_col": self._data_col,
            "label_type": self._label_type,  # String {int|blob|none} to be defined in derived classes
            "row_keys": np.empty(1),  # 1D Numpy array containing UUIDs.
            # Computed in derived classes.
            # This is just a placeholder initialization.
            "split": [
                np.empty(1),
                np.empty(1),
            ]  # List of 1D Numpy arrays. Each array represent a single split.
            # Each element of the array is the index of a correspondig UUID in row_keys
            # split structure must be computed in derived classes.
            # This is just a placeholder initialization
        }

    def get_df_from_metadata(self):
        cs = CassandraSession(self.cass_conf)
        sess = cs.sess

        ## Get rows
        query = f"SELECT * FROM {self._metadata_table};"
        rows = sess.execute(query, execution_profile="dict", timeout=120)
        df = pd.DataFrame(rows)

        return df

    def save_splits(self, out_split_fn="cassandra_split_file.pckl"):
        pickle.dump(self.split_metadata, open(out_split_fn, "wb"))

    def create_splits(self, **kwargs):
        """
        This must be implemented in derived classes
        """
        None
