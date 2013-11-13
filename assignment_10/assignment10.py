from os.path import os, exists
from datetime import datetime, timedelta
from functools import *
import math
import subprocess
import sys
import re
import difflib

pipes = {'stdout':subprocess.PIPE, 'stdin':subprocess.PIPE, 'stderr':subprocess.PIPE}

outputFilename = 'assignment10.txt'
outputFile = open(outputFilename, 'a')
filename = "Cipher.py"
files_to_encrypt = ('encrypt1.txt', 'encrypt2.txt', 'encrypt3.txt')
files_to_decrypt = ('decrypt1.txt', 'decrypt2.txt', 'decrypt3.txt')
dateString = "10-28-2013 23:59:59"

def main():
  out = subprocess.getoutput('ls ./')
  CSIDS = out.split("\n")
  if len(sys.argv) == 3:
    outputFile.write('CSID\tGrade\tComments\n')
    lowerBound = sys.argv[1]
    upperBound = sys.argv[2] + '~';
    myList = []
    count = 0
    for item in CSIDS:
      if lowerBound <= item <= upperBound:
        if "." not in item :
          myList.append( item )
    for csid in myList :
      count += 1
      os.system('clear')
      print('======================')
      print(csid + " " + str(count) + " out of " + str(len(myList)))
      print('======================')
      assign10( csid , True)
  #singleton mode
  else:
    csid = sys.argv[1]
    os.system('clear')
    print('======================')
    print(csid)
    print('======================')
    assign10( csid , False)
  outputFile.close()

def assign10(csid , writeToFile) :
  fileToGrade = ""
  late = 0
  grade = 70
  style = 30
  wrongFileName = False
  header = True
  comments = []

  os.chdir(csid)
  if writeToFile: outputFile.write(csid + "\t")
  files = os.listdir('.')

  #filename checking
  for f in files :
    splitted = subprocess.getoutput('ls -l ' + f).split()
    if f == filename :
      fileToGrade = filename
      late = isLate(splitted)
      break
    elif f == filename.lower() :
      fileToGrade = filename.lower()
      late = isLate(splitted)
      wrongFileName = True
      break

  #really odd filename
  if fileToGrade == "" :
    print(subprocess.getoutput('ls -l'))
    fileToGrade = input("Which file should I grade? ")
    if fileToGrade == "" :
      if writeToFile: 
        outputFile.write("0\tno file\n")
      os.chdir("..")
      return
    else :
      splitted = subprocess.getoutput('ls -l ' + fileToGrade.replace(' ','\ ')).split()
      late = isLate(splitted)
      wrongFileName = True


  # copies ../FILE_TO_COPY to ./ and runs the program in ./
  # diffs output.txt with FILE_CORRECT
  # returns tuple (file output matches, stdout output matches)
  def cp_run_and_diff (stdin_text, file_to_copy, file_correct, stdout_correct):
    os.chdir('..')
    subprocess.getoutput('rm %soutput.txt' % csid)
    os.system('cp %s %sinput.txt' % (file_to_copy, csid))
    os.chdir(csid)
    process = subprocess.Popen(['python3', fileToGrade], **pipes)
    stdout_output = str(process.communicate(bytes(stdin_text, 'UTF-8'))[0])[2:-1]
    differences = subprocess.getoutput('diff output.txt ../%s' % file_correct)
    os.system('rm output.txt')
    os.system('rm input.txt')
    print('stdout: """'+stdout_output+'"""')
    print('diff: """'+differences+'"""')
    return (differences == '', stdout_output == stdout_correct)

  if late != -1:
    # encrypting (3 tests; worth 4 points each; max 15)
    encrypt_tests = []
    # decrypting (3 tests: worth 4 points each; max 15)
    decrypt_tests = []
    # program formatting (1 test: worth 5 points)
    format_test = True
    correct_format = r'Do you want to encrypt or decrypt? (E / D): \nOutput written to output.txt\n'

    for decrypted, encrypted in zip (files_to_encrypt, files_to_decrypt):
      (correctness, format_test1) = cp_run_and_diff ('E', decrypted, encrypted, correct_format)
      encrypt_tests.append(correctness)
      (correctness, format_test2) = cp_run_and_diff ('D', encrypted, decrypted, correct_format)
      decrypt_tests.append(correctness)
      format_test = format_test and format_test1 and format_test2

    
      
    if all(encrypt_tests) and all(decrypt_tests) and format_test:
      print("Perfect! ^_^")
      comments.append("passed all tests (+0)")
    elif not (any(encrypt_tests) or any(decrypt_tests) or format_test):
      print("Failed every test... ='(")
      comments.append("failed all tests (-30)")
      grade -= 30
    else:
      print("Tests failed (Functionality):")
      num_off = 0
      if not encrypt_tests[0]:
        print("\tEncrypt even length")
        comments.append("failed encrypt even (-4)")
        num_off += 4
      if not encrypt_tests[1]:
        print("\tEncrypt odd length")
        comments.append("failed encrypt odd (-4)")
        num_off += 4
      if not encrypt_tests[2]:
        print("\tEncrypt multiple lines")
        comments.append("failed encrypt multi (-4)")
        num_off += 4
      if not decrypt_tests[0]:
        print("\tDecrypt even length")
        comments.append("failed decrypt even (-4)")
        num_off += 4
      if not decrypt_tests[1]:
        print("\tDecrypt odd length")
        comments.append("failed decrypt odd (-4)")
        num_off += 4
      if not decrypt_tests[2]:
        print("\tDecrypt multiple lines")
        comments.append("failed decrypt multi (-4)")
        num_off += 4
      print("Tests failed (Robustness):")
      if not format_test:
        print("\tSTDOUT Formatting")
        comments.append("incorrect formatting (-3)")
        num_off += 3
      grade -= num_off
      print("Total off: (-%d)" % num_off)

  #checking for header and style
  #os.system('vim ' + fileToGrade)
  input("Hit Enter to cat")
  print(subprocess.getoutput('cat ' + fileToGrade))
  headerInput = input("Header and comments? (y/n, hit enter for y): ")
  if headerInput == 'y' or headerInput == '' :
    header = True
  else :
    header = False
  style = input("Style/Other (Out of 30, hit enter for 30): ")
  gen_comments = input("General Comments?: ").rstrip().lstrip()
  gen_comments = gen_comments if len(gen_comments) is not 0 else "looks fine"
  if not style.isdigit() :
    style = 30
  else :
    style = int(style)
  gen_comments += " (%+d)" % (style - 30)
  comments.append("%s" % gen_comments)
  
  #writing grade time!
  if late == -1:
    if writeToFile: outputFile.write('0\t More than 7 days late')
    print('Late more than 7 days!')
  else :
    if late == 3:
      comments.append("3 - 7 days late (-30)")
      grade -= 30
    elif late == 2 :
      comments.append("2 days late (-20)")
      grade -= 20
    elif late == 1 :
      comments.append("1 day late (-10)")
      grade -= 10
    
    if wrongFileName :
      comments.append("wrong filename (-10)")
      grade -= 10
    if not header :
      comments.append("missing comments or malformed header (-10)")
      grade -= 10

    if writeToFile: outputFile.write(str(grade+style) + "\t" + ', '.join(comments))
      
  if writeToFile: outputFile.write('\n')
  os.chdir("..")
      
#returns the number of days late an assignment is
def isLate( splitted ):
  dueDate = datetime.strptime(dateString,"%m-%d-%Y %H:%M:%S")  
  lateOne = dueDate + timedelta(days=1) 
  lateTwo = lateOne + timedelta(days=1)
  lateSev = dueDate + timedelta(days=7)
  turninDate = datetime.strptime(splitted[5] + " " +( ("0" + splitted[6]) if len(splitted[6]) == 1 else splitted[6])+ " " + splitted[7] +" 2013", "%b %d %H:%M %Y")
  if turninDate <= dueDate :
    return 0
  elif turninDate <= lateOne :
    return 1
  elif turninDate <= lateTwo :
    return 2
  elif turninDate <= lateSev:
    return 3
  else :
    return -1

main()