## SSD (Single Shot Multibox Detector)
* Single Shot: Có nghĩa là việc định vị và phân loại đối tượng được thực hiện trên 1 phase duy nhất từ đầu đến cuối.
* MultiBox: Tên của kĩ thuật về bounding box được sử dụng bởi Szegedy et al.
* Detector: Mạng này có khả năng nhận biết và phân loại được đối tượng

### Tổng quan cơ bản:
#### Mô hình chia ra 2 giai đoạn
* Trích xuất feature map (dựa vào mạng cơ sở VGG16)  (để tăng hiệu quả trong việc phát hiện ResNet, InceptionNet, hoặc MobileNet)
* Áp dụng các bộ lọc tích chập để có thể detect được các đối tượng.

#### Kiến trúc mạng được chia phần như ở hình bên dưới.

![image](https://user-images.githubusercontent.com/72034584/158386985-ccbb5488-7c92-4a8e-bb64-48bd7252fd60.png)

