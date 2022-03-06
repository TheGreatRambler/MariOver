# MariOver
The backend of [the Mario Maker 2 API](https://tgrcode.com/mm2/docs/). Hey Nintendo, it's MariOver.

# Setting up
0. Run `pip install -r requirements.txt`
1. Obtain `PRODINFO`, Mario Maker 2 base ticket with console specific data included, and `prod.keys`.
    1. Run `Lockpick_RCM` and download `prod.keys`, which is in `/switch` on your SD card, onto your PC
    2. `PRODINFO` can be obtained using `Memloader`, contained within `Tegra RCM GUI`, combined with `NxNandManager`
    3. Start `Memloader` with `rawNAND` and run `NxNandManager`. Press `Options->Configure keyset` and import your `prod.keys`
    4. Choose the `linux` device in `File->Open drive` and right click `PRODINFO` and click `Decrypt and dump to file`
    5. Close `NxNandManager` and hold the power button on your switch to shut it off
    6. Download `nxdumptool` to your switch and dump the base ticket, downloading it to your PC
    7. Put `PRODINFO.dec`, the base ticket and `prod.keys` into a new folder in this repository named `ConsoleData`
2. Download `TegraExplorer` to your switch and boot into it
    1. Browse EMMC and navigate to `SYSTEM/save/8000000000000010`, copying it to your clipboard. Navigate back to the `sd` card and paste it there
    2. Download that file from your switch and place it in `ConsoleData`
3. Run `python generate_console_data.py`
4. When you update your switch and `NintendoClients` has updated, run `pip install git+https://github.com/kinnay/NintendoClients.git --upgrade` and run `python generate_console_data.py` again

# Running
`uvicorn levelInfoWebserver:app --port 1234` with any port can be used to start the server. Documentation can be found at `http://localhost:1234/docs/`.