#  Copyright (c) 2019 - now, Eggroll Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import time
import unittest
from eggroll.core.pair_store import *
from eggroll.core.pair_store.adapter import PairAdapter
from eggroll.core.pair_store.format import ArrayByteBuffer, PairBinReader, PairBinWriter


class TestPairStore(unittest.TestCase):
    dir = "./"
    # total = 1000 * 1000
    total = 100000
    def _run_case(self, db: PairAdapter):
        start = time.time()
        value = 's' * 1000
        with db.new_batch() as wb:
            for i in range(self.total):
                wb.put(str(i).encode(), value.encode())
        with db.iteritems() as rb:
            cnt = 0
            for k, v in rb:
                if cnt % 100000 == 0:
                    print("item:",cnt, k, v)
                cnt += 1
            print(cnt)
            assert cnt == self.total
        print("time:", time.time() - start)

    def test_lmdb(self):
        with create_pair_adapter({"store_type": STORE_TYPE_LMDB, "path": self.dir + "lmdb"}) as db:
            self._run_case(db)
            db.destroy()

    def test_rocksdb(self):
        with create_pair_adapter({"store_type": STORE_TYPE_ROCKSDB, "path": self.dir + "rocksdb"}) as db:
            self._run_case(db)
            db.destroy()

    def test_file(self):
        with create_pair_adapter({"store_type": STORE_TYPE_FILE, "path": self.dir + "file"}) as db:
            self._run_case(db)
            db.destroy()

    def test_mmap(self):
        with create_pair_adapter({"store_type": STORE_TYPE_MMAP, "path": self.dir + "mmap"}) as db:
            self._run_case(db)
            db.destroy()

    def test_cache(self):
        with create_pair_adapter({"store_type": STORE_TYPE_CACHE, "path": self.dir + "cache"}) as db:
            self._run_case(db)
            db.destroy()

    def test_byte_buffer(self):
        bs = bytearray(1024)
        buf = ArrayByteBuffer(bs)
        buf.write_int32(12)
        buf.write_bytes(b"34")
        buf.set_offset(0)
        assert buf.read_int32() == 12
        assert buf.read_bytes(2) == b"34"

    def test_pair_bin(self):
        bs = bytearray(32)
        buf = ArrayByteBuffer(bs)
        writer = PairBinWriter(buf)
        for i in range(10):
            try:
                writer.write(str(i).encode(), str(i).encode())
            except IndexError as e:
                print(buf.read_bytes(buf.get_offset(), 0))
                buf.set_offset(0)
                writer = PairBinWriter(buf)
                writer.write(str(i).encode(), str(i).encode())
        buf.set_offset(0)
        reader = PairBinReader(buf)
        print("last")
        print(list(reader.read_all()))