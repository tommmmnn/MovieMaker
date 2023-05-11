import tkinter
import windnd
import os
import sys
import cv2
from tkinter.messagebox import showinfo, showerror
from tkinter import ttk
import numpy as np

class MovieMaker:

    def __init__(self) -> None:
        self.tk = tkinter.Tk()
        self.tk.title('MovieMaker')
        try:
            self.tk.iconbitmap(self.current_folder()+os.sep+'moviemaker.ico')
        except Exception as e:
            pass
        self.tk.geometry('820x480')
        windnd.hook_dropfiles(self.tk, func = self.dragged_files)

        self.file_lists = []
        self.input_files_lable = tkinter.Label(self.tk, text='输入文件序列')
        self.input_files_lable.place(relx=0.01, rely=0.01, relwidth=0.618, relheight=0.05)
        self.output_name = tkinter.Listbox(self.tk)
        self.output_name.place(relx=0.01, rely=0.06, relwidth=0.618, relheight=0.93)

        self.listbox_menu = tkinter.Menu(self.output_name, tearoff=0)
        self.listbox_menu.add_command(label="删除", command=self.delete_selected)
        self.output_name.bind("<Button-3>", self.show_listbox_menu)

        # Add the speed and output file name entry widgets
        self.speed_label = tkinter.Label(self.tk, text='视频倍速:')
        self.speed_label.place(relx=0.65, rely=0.1, relwidth=0.1, relheight=0.05)
        self.speed_entry = tkinter.Entry(self.tk)
        self.speed_entry.insert(0, '2')
        self.speed_entry.place(relx=0.75, rely=0.1, relwidth=0.2, relheight=0.05)
        self.output_label = tkinter.Label(self.tk, text='输出文件名:')
        self.output_label.place(relx=0.65, rely=0.2, relwidth=0.1, relheight=0.05)
        self.output_entry = tkinter.Entry(self.tk)
        self.output_entry.insert(0, 'speed_out.avi')
        self.output_entry.place(relx=0.75, rely=0.2, relwidth=0.2, relheight=0.05)

        # Add the process button
        self.process_button = tkinter.Button(self.tk, text='倍速视频', command=self.process_video)
        self.process_button.place(relx=0.65, rely=0.3, relwidth=0.3, relheight=0.1)

        # Add the merge entry widgets
        self.merge_label = tkinter.Label(self.tk, text='输出文件名:')
        self.merge_label.place(relx=0.65, rely=0.5, relwidth=0.1, relheight=0.05)
        self.merge_entry = tkinter.Entry(self.tk)
        self.merge_entry.insert(0, 'merge_out.avi')
        self.merge_entry.place(relx=0.75, rely=0.5, relwidth=0.2, relheight=0.05)

        # Add the merge button
        self.merge_button = tkinter.Button(self.tk, text='合并视频', command=self.merge_video)
        self.merge_button.place(relx=0.65, rely= 0.6, relwidth=0.3, relheight=0.1)
        

        # Add a progress bar
        self.progress_bar = ttk.Progressbar(self.tk, orient='horizontal', mode='determinate')
        self.progress_bar.place(relx=0.01, rely=0.93, relwidth=0.98, relheight=0.05)

    def dragged_files(self, files):
        for file in files:
            if file not in self.file_lists:
                self.file_lists.append(file.decode('gbk'))
                self.output_name.insert(len(self.file_lists)-1, file.decode('gbk'))

    def show_listbox_menu(self, event):
        self.listbox_menu.post(event.x_root, event.y_root)

    def delete_selected(self):
        selected = self.output_name.curselection()
        if len(selected) > 0:
            index = int(selected[0])
            del self.file_lists[index]
            self.output_name.delete(selected)

    def process_video(self):
        # Get the speed and output filename from the entry widgets
        speed = float(self.speed_entry.get())
        if len(self.file_lists) != 1:
            showerror(message='请检查窗口里是否只有一个文件，多余的文件请鼠标右击删除！')
            return
        # Open the input video file
        input_file = self.file_lists[0]
        cap = cv2.VideoCapture(input_file)

        # Get the video frame rate and calculate the output frame rate
        fps = cap.get(cv2.CAP_PROP_FPS)
        output_fps = fps * speed

        # Open the output video file
        output_file = os.path.join(self.current_folder(), self.output_entry.get())
        # output_file = os.path.splitext(input_file)[0] + "_out.avi"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, output_fps, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Calculate the number of output frames
        output_num_frames = int(num_frames / speed)
        for i in range(num_frames):
            ret, frame = cap.read()
            if not ret:
                break

            # Apply speed to the frame
            out.write(frame)
            for j in range(int(speed)-1):
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)

            # Update progress bar
            progress = (i+1) * 100 / output_num_frames
            self.progress_bar['value'] = progress
        showinfo(message=f'输出{output_file}完成！')

    def merge_video(self):
        num_video = len(self.file_lists)
        if num_video < 2 or num_video > 3:
            showerror(message='请检查窗口里是否只有2-3个文件，多余的文件请鼠标右击删除！')
            return
        cap = []
        for file in self.file_lists:
            cap.append(cv2.VideoCapture(file))

        # Get the video properties from the first input video file
        fps = cap[0].get(cv2.CAP_PROP_FPS)
        width = int(cap[0].get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
        num_frames = [int(cap[i].get(cv2.CAP_PROP_FRAME_COUNT)) for i in range(num_video)]
        max_num_frames = max(num_frames)

        # Find the longest input video
        # longest_duration = 0
        # for c in cap:
        #     duration = int(c.get(cv2.CAP_PROP_FRAME_COUNT) / c.get(cv2.CAP_PROP_FPS))
        #     if duration > longest_duration:
        #         longest_duration = duration

        # Calculate the output video properties
        output_width = width * num_video
        output_height = height
        output_fps = fps

        # max_num_frames = int(longest_duration * output_fps)

        # Open the output video file
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_file = os.path.join(self.current_folder(), self.merge_entry.get())
        out = cv2.VideoWriter(output_file, fourcc, output_fps, (output_width, output_height))


        # Open the output video file
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_file = os.path.join(self.current_folder(), self.merge_entry.get())
        # output_file = os.path.splitext(self.file_lists[0])[0] + "_out.avi"
        out = cv2.VideoWriter(output_file, fourcc, output_fps, (output_width, output_height))

        ret = [0]*3
        frame = [0]*3
        lastframe = [0]*3
        for i in range(max_num_frames):
            # Read frames from the input video files
            for j in range(num_video):
                ret[j], frame[j] = cap[j].read()
                if not ret[j]:
                    frame[j] = lastframe[j]
                lastframe[j] = frame[j].copy()
            
            # Create an empty canvas to hold the merged frames
            canvas = np.zeros((output_height, output_width, 3), dtype=np.uint8)

            # Merge the frames onto the canvas
            if num_video == 2:
                canvas[:, :width, :] = frame[0]
                canvas[:, width:, :] = frame[1]
            # Merge the frames onto the canvas
            if num_video == 3:
                canvas[:, :width, :] = frame[0]
                canvas[:, width:2*width, :] = frame[1]
                canvas[:, 2*width:, :] = frame[2]


            # Write the merged frame to the output video file
            out.write(canvas)

            # Update progress bar
            progress = (i + 1) * 100 / max_num_frames
            self.progress_bar['value'] = progress
        showinfo(message=f'输出{output_file}完成！')

        # Release the resources
        for c in cap:
            c.release()
        out.release()
        # cv2.destroyAllWindows()


    def current_folder(self):
        return os.path.dirname(os.path.realpath(sys.executable))

    def run(self):
        self.tk.mainloop()

if __name__ == '__main__':
    mm = MovieMaker()
    mm.run()
