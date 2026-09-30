# 🧋 Pearl Milk Tea — เว็บร้านชานมไข่มุกด้วย Python

## สิ่งที่เว็บนี้ทำได้
- หน้าแรกแสดงเมนูชานม
- สมัครสมาชิกด้วย username/password
- รหัสผ่านถูกเก็บแบบ hash ไม่ได้เก็บเป็นข้อความตรง ๆ
- Login / Logout
- เลือกขนาด S/M/L
- เลือกความหวาน
- เลือกระดับน้ำแข็ง
- เลือกท็อปปิ้ง
- เพิ่มหลายแก้วลงตะกร้า
- ลบสินค้าออกจากตะกร้า
- Checkout พร้อมที่อยู่และหมายเหตุ
- บันทึกออเดอร์ลง SQLite
- ดูประวัติการสั่งซื้อ

## วิธีเปิดใน Windows + VS Code

### 1. เปิดโฟลเดอร์โปรเจกต์
แตกไฟล์ ZIP แล้วเปิดโฟลเดอร์ `bubble_tea_shop` ใน VS Code

### 2. เปิด Terminal
VS Code > Terminal > New Terminal

### 3. สร้าง Virtual Environment
ถ้า `python` ใช้ไม่ได้ ให้ใช้ Python path ที่ติดตั้งไว้ เช่น:

`& "C:\Users\plmnp\AppData\Local\Python\bin\python.exe" -m venv .venv`

จากนั้นเปิดใช้งาน:

`.venv\Scripts\Activate.ps1`

ถ้าเห็น `(.venv)` หน้า prompt แปลว่าเปิดสำเร็จ

### 4. ติดตั้ง Flask
`python -m pip install -r requirements.txt`

ถ้า `python` ในเครื่องยังชี้ผิด ให้ใช้:

`& "C:\Users\plmnp\AppData\Local\Python\bin\python.exe" -m pip install -r requirements.txt`

### 5. รันเว็บ
`python app.py`

หรือถ้าต้องใช้ Python path แบบเต็ม:

`& "C:\Users\plmnp\AppData\Local\Python\bin\python.exe" app.py`

### 6. เปิดเว็บ
เปิด Chrome แล้วเข้า:

`http://127.0.0.1:5000`

## ลำดับการทดลอง
1. กด สมัครสมาชิก
2. สร้าง username/password
3. Login
4. เลือกเมนู
5. เลือกไซซ์
6. เลือกความหวาน
7. เลือกน้ำแข็ง
8. เลือกท็อปปิ้ง
9. กดเพิ่มลงตะกร้า
10. ไปตะกร้า
11. กดดำเนินการสั่งซื้อ
12. กรอกที่อยู่
13. ยืนยัน
14. เปิด "ออเดอร์ของฉัน" เพื่อดูรายการ

## หมายเหตุ
โปรเจกต์นี้เป็นเว็บฝึกทำงานแบบ local ก่อน ยังไม่มีระบบชำระเงินจริง, ระบบแอดมิน, รูปสินค้า, สต็อก และการส่งออเดอร์ไป LINE/ระบบขนส่ง

ก่อนนำไปใช้งานจริงควรเปลี่ยน `app.secret_key` เป็นค่าสุ่มที่ปลอดภัย และตั้งค่า production ให้เหมาะสม
