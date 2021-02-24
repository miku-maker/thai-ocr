วิธีใช้
1. pull project โดยใช้คำสั่ง git clone https://github.com/miku-maker/thai-ocr.git
2. สร้าง image docker โดยใช้คำสั่ง docker build .
3. รัน docker image โดยใช้คำสั่ง docker run -p 80:80 -it {image id}
   คำอธิบาย -p หมายถึง mapping port คือ ข้างใน image รันผ่าน port 80 เราจะแมพออกมาข้างนอกโดยใช้ port 80 --> external:internal
   คำอธิบาย -it หมายถึงรันโดยใช้ image หรือ container 
5. วิธีปิด Ctrl+c 
6. ลบ container โดยใช้คำสั่ง docker rm {container id}
7. ลบ docker images โดยใช้คำสั่ง docker rmi {image id}
