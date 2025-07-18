
# Cài đặt thư viện
pip install -r requirements.txt

# Chạy chương trình
python app.py

# Giới thiệu
Trình trực quan hóa thuật toán tìm đường bằng Pygame trên Mê cung (MAZE)
Ứng dụng này trực quan hóa các thuật toán tìm đường (Dijkstra, A*, BFS, DFS) trên lưới (grid) bằng thư viện Pygame.
Người dùng có thể tương tác để đặt tường, điểm bắt đầu và điểm kết thúc, tạo mê cung và quan sát quá trình chạy của thuật toán từng bước một.

Tính năng:
Lưới tương tác để vẽ/xóa tường.

Có thể di chuyển điểm bắt đầu/kết thúc bằng chuột.

Trực quan hóa các thuật toán: Dijkstra, A*, BFS, và DFS.

Hỗ trợ tạo mê cung tự động và xóa lưới.

Hiển thị thời gian thực thi và lịch sử các lần chạy gần nhất.

Phím điều khiển:
Chuột trái + kéo: Vẽ/xóa tường.

Chuột phải: Di chuyển điểm bắt đầu.

Chuột giữa: Di chuyển điểm kết thúc.

Phím 1/2/3/4: Chuyển đổi thuật toán (Dijkstra/A*/DFS/BFS).

Phím SPACE: Bắt đầu trực quan hóa thuật toán.

Phím TAB: Tạo mê cung ngẫu nhiên.

Phím ` (backquote): Xóa toàn bộ lưới.

Các mô-đun sử dụng:
pygame: Xử lý giao diện và tương tác người dùng.

algorithms: Triển khai các thuật toán tìm đường theo từng bước.

maze_generators: Tiện ích tạo mê cung.

Thành phần chính:
Trạng thái và hiển thị lưới.

Xử lý sự kiện từ chuột và bàn phím.

Chạy thuật toán từng bước và trực quan hóa.

Theo dõi và hiển thị lịch sử chạy gần đây.

