with open('0_0_input','w') as f:
  f.write('CONNECT localhost 9000\n')
  f.write('GET existing_file\n')
  f.write('GET non_existent_file\n')
  f.write('GET a_dir/nested_existing_file')
#
with open('0_0_output_client','w') as f:
  f.write('CONNECT classroom.cs.unc.edu 9000\n')
  f.write('CONNECT accepted for FTP server at host classroom.cs.unc.edu and port 9000\n')
  f.write('FTP reply 220 accepted. Text is: COMP 431 FTP server ready.\n')
  f.write('USER anonymous\r\n')
  f.write('FTP reply 331 accepted. Text is: Guest access OK, send password.\n')
  f.write('PASS guest@\r\n')
  f.write('FTP reply 230 accepted. Text is: Guest login OK.\n')
  f.write('SYST\r\n')
  f.write('FTP reply 215 accepted. Text is: UNIX Type: L8.\n')
  f.write('TYPE I\r\n')
  f.write('FTP reply 200 accepted. Text is: Type set to I.\n')
  f.write('QUIT\n')
  f.write('QUIT accepted, terminating FTP client\n')
  f.write('QUIT\r\n')
  f.write('FTP reply 221 accepted. Text is: Goodbye.\n')
  f.write('')

with open('0_0_output_server','w') as f:
  f.write('220 COMP 431 FTP server ready.\r\n')
  f.write('USER anonymous\r\n')
  f.write('331 Guest access OK, send password.\r\n')
  f.write('PASS guest@\r\n')
  f.write('230 Guest login OK.\r\n')
  f.write('SYST\r\n')
  f.write('215 UNIX Type: L8.\r\n')
  f.write('TYPE I\r\n')
  f.write('200 Type set to I.\r\n')
  f.write('QUIT\r\n')
  f.write('221 Goodbye.\r\n')
  f.write('')
