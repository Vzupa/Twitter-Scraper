import tkinter as tk
from tkinter import filedialog
import pandas as pd


def csv_to_dataframe(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error: {e}")


class TweetWindow(tk.Toplevel):
    def __init__(self, tweet_data):
        super().__init__()
        self.geometry("600x200")
        self.title("Window tweeta :)")
        text = tk.Text(self, height=10, width=500)
        text.pack()

        print(tweet_data)

        text.insert(tk.END, f"Uporabnisko ime :  {tweet_data['Uporabnisko ime'].values.item()} \n")
        text.insert(tk.END, f"Handle: {tweet_data['Handle'].values.item()}\n")
        text.insert(tk.END, f"Cas :  {tweet_data['Cas'].values.item()}\n")
        text.insert(tk.END, f"Body : \n  {tweet_data['Body'].values.item()}\n \n")

        print("smt")


class App:
    def __init__(self, master):
        self.master = master
        master.title("CSV File Uploader")
        master.geometry("1000x800")

        # Create left frame to hold fields and buttons
        left_frame = tk.Frame(master, width=100, height=800)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        # Create labels and entries for file name and file data
        self.file1_name_label = tk.Label(left_frame, text="Naložena prva datoteka:")
        self.file1_name_label.pack()
        self.file1_name_entry = tk.Entry(left_frame)
        self.file1_name_entry.pack()

        # Create button to upload first CSV file
        self.upload_button1 = tk.Button(left_frame, text="Naloži prvo datoteko:", command=self.upload_csv1)
        self.upload_button1.pack()

        self.file2_name_label = tk.Label(left_frame, text="Naložena druga datoteka:")
        self.file2_name_label.pack()
        self.file2_name_entry = tk.Entry(left_frame)
        self.file2_name_entry.pack()

        # Create button to upload second CSV file
        self.upload_button2 = tk.Button(left_frame, text="Naloži drugo datoteko:", command=self.upload_csv2)
        self.upload_button2.pack()

        # Create button to start processing
        self.start_button = tk.Button(left_frame, text="Primerjaj datoteki", command=self.zacniObdelavo)
        self.start_button.pack()

        # Initialize variable to hold name of uploaded files
        self.file1_name = ""
        self.file2_name = ""

        # Create a new window to display tweet data
        self.tweet_data_window = tk.Toplevel(master)
        self.tweet_data_window.title("Tweet Data")

        # Create a label to display the tweet data
        self.tweet_data_label = tk.Label(self.tweet_data_window, text="")
        self.tweet_data_label.pack(fill=tk.BOTH, expand=True)

        # Create listbox to hold tweet data
        self.prva_datoteka = tk.Label(text="Vsebina prve datoteke:").pack()
        self.listbox1 = tk.Listbox(master)
        self.listbox1.pack(fill=tk.BOTH, expand=True)
        self.listbox1.bind("<Double-Button-1>", self.show_tweet_data)

        self.druga_datoteka = tk.Label(text="Vsebina druge datoteke:").pack()
        self.listbox2 = tk.Listbox(master)
        self.listbox2.pack(fill=tk.BOTH, expand=True)
        self.listbox2.bind("<Double-Button-1>", self.show_tweet_data2)

        # Create listbox to hold deleted tweet data
        self.primerjava = tk.Label(text="Izbrisani tweeti:").pack()
        self.listbox = tk.Listbox(master)
        self.listbox.pack(fill=tk.BOTH, expand=True)

    def upload_csv1(self):
        # Open file dialog to select CSV file
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

        # Store name of uploaded file in file1_name_entry and file1_name variable
        self.file1_name = file_path
        self.file1_name_entry.delete(0, tk.END)
        self.file1_name_entry.insert(0, self.file1_name)

    def upload_csv2(self):
        # Open file dialog to select CSV file
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

        # Store name of uploaded file in file2_name_entry and file2_name variable
        self.file2_name = file_path
        self.file2_name_entry.delete(0, tk.END)
        self.file2_name_entry.insert(0, self.file2_name)

    def zacniObdelavo(self):
        # Check if both files are uploaded
        print(self.file1_name)
        print(self.file2_name)

        if self.file1_name and self.file2_name:
            # Load CSV files into Pandas dataframes
            df1 = csv_to_dataframe(self.file1_name)
            df2 = csv_to_dataframe(self.file2_name)

            # Identify the younger and older CSV files
            if (self.file1_name) < (self.file2_name):
                younger_df = df1
                older_df = df2

            else:
                younger_df = df2
                older_df = df1
            self.younger_df = younger_df
            self.older_df = older_df
            try:
                is_present = younger_df['Cas'].isin(older_df['Cas'])

                # select the tweets from older_tweets that are not present in younger_tweets
                non_duplicate_tweets = younger_df[~is_present]

                # store the body of non-duplicate tweets in an array
                tweet_bodies = non_duplicate_tweets['Body'].values
                print(len(tweet_bodies))
                self.tweet_bodies = tweet_bodies
                for tweet in tweet_bodies:
                    self.listbox.insert(tk.END, tweet)
                    self.listbox.itemconfig(tk.END, bg="misty rose")
                tb1 = older_df["Body"].values
                tb2 = younger_df["Body"].values
                for tweet in tb2:
                    if tweet in tweet_bodies:
                        self.listbox1.insert(tk.END, tweet)
                        self.listbox1.itemconfig(tk.END, bg="misty rose")

                    else:
                        self.listbox1.insert(tk.END, tweet)

                for tweet in tb1:
                    self.listbox2.insert(tk.END, tweet)
            except Exception as e:
                print(e)


        else:
            print("Please upload both CSV files.")

    def show_tweet_data(self, event):
        # Get the selected item in the listbox
        selected_item = self.listbox1.get(self.listbox1.curselection())

        # Parse the tweet data from the selected item

        tweet_data = self.younger_df.loc[self.younger_df['Body'] == selected_item]

        tweet_window = TweetWindow(tweet_data)

    def show_tweet_data2(self, event):
        selected_item = self.listbox2.get(self.listbox2.curselection())
        tweet_data = self.older_df.loc[self.older_df['Body'] == selected_item]

        tweet_window = TweetWindow(tweet_data)


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
