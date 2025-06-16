# MariOver
The backend of [The Mario Maker 2 API](https://tgrcode.com/mm2/docs/). Hey Nintendo, it's MariOver.

For more reading materials on this project check out:
* [Mario Maker 2 Comments](https://tgrcode.com/posts/mario_maker_2_comments)
* [Mario Maker 2 Datasets](https://tgrcode.com/posts/mario_maker_2_datasets)
* [A Mario ML Diffusion Model](https://tgrcode.com/posts/a_mario_ml_diffusion_model)
* [Mario Maker 2 Ninjis](https://tgrcode.com/posts/mario_maker_2_ninjis)

# Setting up
0. Run `pip install -r requirements.txt`
1. Obtain `PRODINFO` and `prod.keys`.
    1. Run `Lockpick_RCM` and download `prod.keys`, which is in `/switch` on your SD card, onto your PC
    2. `PRODINFO` can be obtained using `Memloader`, contained within `Tegra RCM GUI`, combined with `NxNandManager`
    3. Start `Memloader` with `rawNAND` and run `NxNandManager`. Press `Options->Configure keyset` and import your `prod.keys`
    4. Choose the `linux` device in `File->Open drive` and right click `PRODINFO` and click `Decrypt and dump to file`
    5. Close `NxNandManager` and hold the power button on your switch to shut it off
    7. Put `PRODINFO.dec` and `prod.keys` into a new folder in this repository named `ConsoleData`
2. Obtain `8000000000000010` and `8000000000000110`
    1. Download `TegraExplorer` to your switch and boot into it
    2. Browse EMMC and navigate to `SYSTEM/save/8000000000000010`, copying it to your clipboard. Navigate back to the `sd` card and paste it there
    3. Download that file from your switch and place it in `ConsoleData`
    4. Repeat with `SYSTEM/save/8000000000000110`
3. Run `python generate_console_data.py`
4. Add the 2 letter country code of the host switch to `webserver_args.json` if it is not `US`
4. When you update your switch and `NintendoClients` has updated, run `pip install git+https://github.com/kinnay/NintendoClients.git --upgrade` and run `python generate_console_data.py` again

# Running
`uvicorn mariover:app --port 1234` with any port can be used to start the server. Documentation can be found at `http://localhost:1234/docs/`.