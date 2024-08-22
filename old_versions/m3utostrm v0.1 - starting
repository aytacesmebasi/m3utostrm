import os

#Create output_files folder
current_working_directory = os.getcwd()
output_folder_path = os.path.join(current_working_directory, 'output_files')
os.makedirs(output_folder_path, exist_ok=True)
strm_folder_path = os.path.join(current_working_directory, 'strm_files')
os.makedirs(strm_folder_path, exist_ok=True)

# Specify the M3U file path (using raw string or forward slash)
m3u_file_path = os.path.join(output_folder_path, 'tobeprocess.m3u')

# Create a folder to save STRM files
os.makedirs(strm_folder_path, exist_ok=True)

# Read M3U file and create STRM files
with open(m3u_file_path, 'r', encoding='utf-8') as m3u_file:
    lines = m3u_file.readlines()
    
    i = 0
    while i < len(lines):
        extinf_line = lines[i].strip()
        
        # If the line starts with #EXTINF, treat the next line as the URL
        if extinf_line.startswith('#EXTINF:'):
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                file_name = extinf_line.split(',', 1)[1] + '.strm'
                file_path = os.path.join(strm_folder_path, file_name)
                
                # Create the STRM file and write the URL in it
                with open(file_path, 'w', encoding='utf-8') as strm_file:
                    strm_file.write(url_line)
                
                i += 2  # Jump to next #EXTINF line
            else:
                print(f"Warning: URL for {extinf_line} is missing.")
                i += 1  # We're in the last row, just move on
        else:
            print(f"Warning: #EXTINF line expected for {extinf_line}.")
            i += 1  # Skip this line and go to the next line

print("STRM files were created successfully.")
