import os

# 定义需要转换的文件扩展名
extensions = ['.json', '.md', '.yaml']

# 定义一个函数来转换文件的行尾
def convert_line_endings_to_crlf(file_path):
    # 读取原始文件内容
    with open(file_path, 'rb') as file:
        content = file.read()
    
    # 将LF转换为CRLF
    content = content.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    
    # 写回转换后的内容
    with open(file_path, 'wb') as file:
        file.write(content)

# 定义一个函数来递归遍历目录
def traverse_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件扩展名是否需要转换
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                print(f"Converting {file_path}")
                # 转换文件的行尾
                convert_line_endings_to_crlf(file_path)

# 从当前目录开始递归遍历
if __name__ == "__main__":
    traverse_directory('.')
