#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from ScrollableNotebook import *
import os
import png

#global:
g_PNGStruct = None
g_CurrentPath = None

#handlers:
def closeProgram():
    global root
    root.destroy()

def openPng():
    filePath = filedialog.askopenfilename(title="Open PNG file", filetypes=(("PNG file", "*.png"), ("All files", "*")))
    if not filePath:
        return #user has reject file open dialog
    
    pngBytes = None
    try:
        file = open(filePath, "rb")
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0, os.SEEK_SET)
        pngBytes = file.read(size)
        file.close()
    except:
        messagebox.showerror("File error", "Can't open file")
        return
    
    if not pngBytes:
        messagebox.showerror("Data error", "There is no data to read in the file")
        return
    
    struct = png.PNGStruct(pngBytes)
    if not struct.parse():
        messagebox.showerror("Data error", "The byte sequence could not be read as a PNG format structure")
        return
    
    global g_PNGStruct
    global g_CurrentPath
    g_PNGStruct = struct
    g_CurrentPath = filePath
    resetWinTitle(g_CurrentPath)
    printPNGStruct(g_PNGStruct)
    resetStatusBar(g_PNGStruct)

def closePng():
    global g_PNGStruct
    global g_CurrentPath
    g_PNGStruct = g_CurrentPath = None
    resetWinTitle()
    printPNGStruct()
    resetStatusBar()

def exportToTxt():
    global g_PNGStruct
    global g_CurrentPath

    if not g_PNGStruct or not g_CurrentPath:
        messagebox.showerror("No data", "There is no data to export")
        return
    file = filedialog.asksaveasfile(title="Save PNG info")
    if not file:
        return
    
    file.write(f"PNG path: {g_CurrentPath}")
    file.write(f"\nTotal size, kb: {round(g_PNGStruct.totalSize / 1024, 1)}")
    file.write(f"\nChunk count: {len(g_PNGStruct.chunks)}")
    file.write("\n\n")

    for chunk in g_PNGStruct.chunks:
        file.write(f"{chunk.name}:")

        if type(chunk) == png.PNGIHDRChunk:
            file.write(f"\nWidth: {chunk.width}")
            file.write(f"\nHeight: {chunk.height}")
            file.write(f"\nBit depth: {chunk.bitDepth}")
            file.write(f"\nColor type: {chunk.colorTypeStr}")
            file.write(f"\nCompression: {chunk.compressionStr}")
            file.write(f"\nFiltering: {chunk.filtering}")
            file.write(f"\nInterlace: {chunk.interlaceStr}")

        elif type(chunk) == png.PNGTEXTChunk:
            file.write(f"\nKeyword: {chunk.key}\nText: {chunk.text}")

        elif type(chunk) == png.PNGBKGDChunk:
            if chunk.type == png.PNGBKGDChunk.TYPE_INDEX:
                file.write(f"\nIndex: {chunk.index}")
            elif chunk.type == png.PNGBKGDChunk.TYPE_GRAYSCALE:
                file.write(f"\nGray level: {chunk.value}")
            elif chunk.type == png.PNGBKGDChunk.TYPE_TRUECOLOR:
                file.write(f"\nRed: {chunk.red}\nGreen: {chunk.green}\nBlue: {chunk.blue}")

        else:
            file.write("\nSome binary data...")

        file.write(f"\nCRC: {hex(chunk.crc)}")
        file.write("\n\n")

    file.close()
    messagebox.showinfo("Success", "The data was exported successfully")
    

#print png struct to GUI
#creates layout and controls which contains png information
def printPNGStruct(struct = None):

    #delete all tabs:
    for tabId in tabBar.tabs():
        tabBar.forget(tabId)

    if not struct:
        return

    #fill tab content:
    for chunk in struct.chunks:
        frame = ttk.Frame(tabBar)

        info = "" #chunk printable text information

        if type(chunk) == png.PNGIHDRChunk:
            info = f"Width: {chunk.width}\nHeight: {chunk.height}\nBitDepth: {chunk.bitDepth}\n" + \
            f"Color type: {chunk.colorTypeStr}\nCompression: {chunk.compressionStr}\n" + \
            f"Filtering: {chunk.filtering}\nInterlace: {chunk.interlaceStr}"

        elif type(chunk) == png.PNGTEXTChunk:
            info = f"Keyword: {chunk.key}\nText: {chunk.text}"

        elif type(chunk) == png.PNGBKGDChunk:
            if chunk.type == png.PNGBKGDChunk.TYPE_INDEX:
                info = f"Index: {chunk.index}"
            elif chunk.type == png.PNGBKGDChunk.TYPE_GRAYSCALE:
                info = f"Gray level: {chunk.value}"
            elif chunk.type == png.PNGBKGDChunk.TYPE_TRUECOLOR:
                info = f"Red: {chunk.red}\nGreen: {chunk.green}\nBlue: {chunk.blue}"

        elif type(chunk) == png.PNGPHYSChunk:
            info = f"PixelsPerUnitX: {chunk.ppx}\nPixelsPerUnitY: {chunk.ppy}\nUnitSpecifier: {chunk.unitStr}"

        elif type(chunk) == png.PNGGAMAChunk:
            info = f"Gamma: {chunk.gamma}"

        else:
            info = "It is impossible to display the content \n(the visualization of the current type of chunk is unsupported" + \
            f"\nor the chunk cannot be visualized in human-readable form)"

        info += f"\n\n{hex(chunk.crc)}"

        lbl = ttk.Label(frame, text=info)
        lbl.pack(fill="both", padx=5, pady=5)
        frame.pack(fill="both", expand=True)
        tabBar.add(frame, text=chunk.name)

def resetStatusBar(struct = None):
    if struct:
        lblStatusBar["text"] = f"PNG size, kb: {round(struct.totalSize / 1024, 1)} | Chunk count: {len(struct.chunks)}"
    else:
        lblStatusBar["text"] = ""

def resetWinTitle(path = None):
    winTitle = "PNG Struct"
    if path:
        root.title(f"{winTitle}: {path}")
    else:
        root.title(f"{winTitle}")

#gui:
root = tk.Tk()
root.title("PNG struct")

mainMenu = tk.Menu(tearoff=0)
fileMenu = tk.Menu(tearoff=0)
fileMenu.add_command(label="Open PNG", command=openPng)
fileMenu.add_command(label="Close", command=closePng)
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=closeProgram)
exportMenu = tk.Menu(tearoff=0)
exportMenu.add_command(label="To .txt", command=exportToTxt)
mainMenu.add_cascade(label="File", menu=fileMenu)
mainMenu.add_cascade(label="Export", menu=exportMenu)

tabBar = ScrollableNotebook(root, wheelscroll=True)
tabBar.pack(expand=True, fill="both")

lblStatusBar = ttk.Label()
lblStatusBar.pack(fill=X, padx=3, pady=3)

root.geometry("500x300")
root.config(menu=mainMenu)
root.protocol("WM_DELETE_WINDOW", closeProgram)

root.mainloop()