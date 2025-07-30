import os
import shutil
import unittest

class TestDataDirectory(unittest.TestCase):
    def setUp(self):
        # Xóa các thư mục data sai vị trí trước khi test
        self.wrong_data_dirs = [
            os.path.join(os.path.dirname(__file__), 'data'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'),
        ]
        for d in self.wrong_data_dirs:
            if os.path.exists(d):
                shutil.rmtree(d)

    def test_no_wrong_data_dir_created(self):
        # Chạy lại các service tạo data
        from services.user_summary.summary_update import SummaryUpdateManager
        manager = SummaryUpdateManager(prompts_dir='dummy', config_dir='dummy', llm_service=None)
        # Kiểm tra không có thư mục data nào bị tạo sai vị trí
        for d in self.wrong_data_dirs:
            self.assertFalse(os.path.exists(d), f"Sai: Tồn tại thư mục data ở {d}")

if __name__ == "__main__":
    unittest.main()
