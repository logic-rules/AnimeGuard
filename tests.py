import os

files = os.listdir("input")
print("All files in input:", files)


first_file = files[0]
print("First file:", first_file)

path = os.path.join("input", first_file)
os.remove(path)