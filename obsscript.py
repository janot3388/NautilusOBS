import obspython as obs
from datetime import datetime
import os
import subprocess

def script_update(context, settings):
    context = obs.context()
    settings = obs.obs_data_create()
    obs.obs_get_source_by_name("NOME_DA_SOURCE_DA_GRAVAÇÃO", settings, context)
    if obs.obs_source_active(settings):
        pass
    else:
        # Check if the current time is midnight
        now = datetime.now()
        if now.hour == 0 and now.minute == 0 and now.second == 0:
            compress_recordings()
            move_and_rename_recordings()
            delete_old_recordings()
            create_folders()

def compress_recordings():
    root_path = "DIRETÓRIO_DAS_GRAVAÇÕES"
    for file in os.listdir(root_path):
        if file.endswith(".mp4"):
            input_file = os.path.join(root_path, file)
            output_file = os.path.join(root_path, "compressed_" + file)
            subprocess.call(["ffmpeg", "-i", input_file, "-b:v", "1200k", output_file])
            os.remove(input_file)
            
def move_and_rename_recordings():
    root_path = "DIRETÓRIO_DAS_GRAVAÇÕES"
    for file in os.listdir(root_path):
        if file.startswith("compressed_"):
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            source_path = os.path.join(root_path, file)
            new_file_name = current_time
            year_path = os.path.join(root_path, current_time.strftime("%Y"))
            month_path = os.path.join(year_path, current_time.strftime("%m"))
            if not os.path.exists(year_path):
                os.mkdir(year_path)
            if not os.path.exists(month_path):
                os.mkdir(month_path)
            destination_path = os.path.join(month_path, new_file_name)
            os.rename(source_path, destination_path)

def delete_old_recordings():
    root_path = "DIRETÓRIO_DAS_GRAVAÇÕES"
    total_size = 0
    for path, dirs, files in os.walk(root_path):
        for f in files:
            fp = os.path.join(path, f)
            total_size += os.path.getsize(fp)
    threshold_size = 100000000 # 100MB
    if total_size > threshold_size:
        for file in os.listdir(root_path):
            file_path = os.path.join(root_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
def create_folders():
    root_path = "DIRETÓRIO_DAS_GRAVAÇÕES"
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    year_path = os.path.join(root_path, current_time.strftime("%Y"))
    month_path = os.path.join(year_path, current_time.strftime("%m"))
    if not os.path.exists(year_path):
        os.mkdir(year_path)
    if not os.path.exists(month_path):
        os.mkdir(month_path)
    return month_path
        

if __name__ == "__main__":
    while True:
        # Start OBS recording
        obs.start_recording()
        
        # Wait for the recording to end (assume it ends at midnight)
        now = datetime.now()
        next_day = datetime(now.year, now.month, now.day+1)
        time_to_wait = (next_day - now).total_seconds()
        time.sleep(time_to_wait)
        
        # Stop OBS recording
        obs.stop_recording()
        
        # Compress the recording
        obs.compress_recording(quality=1200)
        
        # Move the recording to the correct folder
        month_path = create_folders()
        obs.move_recording(month_path)
        
        # Delete old recordings
        delete_old_recordings()


