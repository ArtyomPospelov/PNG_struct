# PNG struct
![image](https://github.com/user-attachments/assets/852400c0-edec-4a16-a29f-6be278796fd8)
## Description:
A small utility that allows you to read the binary structure of the PNG image format.
## Project Features:
1. Written in Python3 (version 3.10), Tkinter library;
2. Thanks to the user muhammeteminturgut (https://github.com/muhammeteminturgut). He wrote an add-on over ttk.Notebook that allows you to scroll through tabs of the standard tkinter control of the same name;
3. The OOP approach is used to read the PNG structure: A convenient class has been created for passing through bytes in the file. The data itself is encapsulated in special classes. A separate subclass has been created for each PNG chunk. You can reuse byteWalker.py and png.py for your projects, these are modules;
4. The project itself is very raw. As for the GUI part, the code is not very good there - I tried to write it quickly, it was much more interesting to write a png module, get acquainted with the binary structure of a png file. Perhaps sometime (if necessary) I will finalize the project.
