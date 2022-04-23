meta:
  id: level
  endian: le
seq:
  - id: start_y
    type: u1
    doc: Starting Y position of level
  - id: goal_y
    type: u1
    doc: Y position of goal
  - id: goal_x
    type: s2
    doc: X position of goal
  - id: timer
    type: s2
    doc: Starting timer
  - id: clear_condition_magnitude
    type: s2
    doc: Clear condition magnitude
  - id: year
    type: s2
    doc: Year made
  - id: month
    type: s1
    doc: Month made
  - id: day
    type: s1
    doc: Day made
  - id: hour
    type: s1
    doc: Hour made
  - id: minute
    type: s1
    doc: Minute made
  - id: autoscroll_speed
    type: u1
    enum: autoscroll_speed
    doc: Autoscroll speed
  - id: clear_condition_category
    type: u1
    enum: clear_condition_category
    doc: Clear condition category
  - id: clear_condition
    type: s4
    enum: clear_condition
    doc: Clear condition
  - id: unk_gamever
    type: s4
    doc: Unknown gamever
  - id: unk_management_flags
    type: s4
    doc: Unknown management_flags
  - id: clear_attempts
    type: s4
    doc: Clear attempts
  - id: clear_time
    type: s4
    doc: Clear time
  - id: unk_creation_id
    type: u4
    doc: Unknown creation_id
  - id: unk_upload_id
    type: s8
    doc: Unknown upload_id
  - id: game_version
    type: s4
    enum: game_version
    doc: Game version level was made in
  - id: unk1
    size: 0xBD
  - id: gamestyle
    type: s2
    enum: gamestyle
    doc: Game style
  - id: unk2
    type: u1
  - id: name
    type: str
    size: 0x42
    encoding: UTF-16LE
  - id: description
    type: str
    size: 0xCA
    encoding: UTF-16LE
  - id: overworld
    type: map
  - id: subworld
    type: map
enums:
  gamestyle:
    12621: smb1
    13133: smb3
    22349: smw
    21847: nsmbw
    22323: sm3dw
  clear_condition_category:
    0: none
    1: parts
    2: status
    3: actions
  game_version:
    0: v1_0_0
    1: v1_0_1
    2: v1_1_0
    3: v2_0_0
    4: v3_0_0
    5: v3_0_1
    33: unk
  clear_condition:
    0: none
    137525990: reach_the_goal_without_landing_after_leaving_the_ground
    199585683: reach_the_goal_after_defeating_at_least_all_mechakoopa
    272349836: reach_the_goal_after_defeating_at_least_all_cheep_cheep
    375673178: reach_the_goal_without_taking_damage
    426197923: reach_the_goal_as_boomerang_mario
    436833616: reach_the_goal_while_wearing_a_shoe
    713979835: reach_the_goal_as_fire_mario
    744927294: reach_the_goal_as_frog_mario
    751004331: reach_the_goal_after_defeating_at_least_all_larry
    900050759: reach_the_goal_as_raccoon_mario
    947659466: reach_the_goal_after_defeating_at_least_all_blooper
    976173462: reach_the_goal_as_propeller_mario
    994686866: reach_the_goal_while_wearing_a_propeller_box
    998904081: reach_the_goal_after_defeating_at_least_all_spike
    1008094897: reach_the_goal_after_defeating_at_least_all_boom_boom
    1051433633: reach_the_goal_while_holding_a_koopa_shell
    1061233896: reach_the_goal_after_defeating_at_least_all_porcupuffer
    1062253843: reach_the_goal_after_defeating_at_least_all_charvaargh
    1079889509: reach_the_goal_after_defeating_at_least_all_bullet_bill
    1080535886: reach_the_goal_after_defeating_at_least_all_bully_bullies
    1151250770: reach_the_goal_while_wearing_a_goomba_mask
    1182464856: reach_the_goal_after_defeating_at_least_all_hop_chops
    1219761531: reach_the_goal_while_holding_a_red_pow_block_or_reach_the_goal_after_activating_at_least_all_red_pow_block
    1221661152: reach_the_goal_after_defeating_at_least_all_bob_omb
    1259427138: reach_the_goal_after_defeating_at_least_all_spiny_spinies
    1268255615: reach_the_goal_after_defeating_at_least_all_bowser_meowser
    1279580818: reach_the_goal_after_defeating_at_least_all_ant_trooper
    1283945123: reach_the_goal_on_a_lakitus_cloud
    1344044032: reach_the_goal_after_defeating_at_least_all_boo
    1425973877: reach_the_goal_after_defeating_at_least_all_roy
    1429902736: reach_the_goal_while_holding_a_trampoline
    1431944825: reach_the_goal_after_defeating_at_least_all_morton
    1446467058: reach_the_goal_after_defeating_at_least_all_fish_bone
    1510495760: reach_the_goal_after_defeating_at_least_all_monty_mole
    1656179347: reach_the_goal_after_picking_up_at_least_all_1_up_mushroom
    1665820273: reach_the_goal_after_defeating_at_least_all_hammer_bro
    1676924210: reach_the_goal_after_hitting_at_least_all_p_switch_or_reach_the_goal_while_holding_a_p_switch
    1715960804: reach_the_goal_after_activating_at_least_all_pow_block_or_reach_the_goal_while_holding_a_pow_block
    1724036958: reach_the_goal_after_defeating_at_least_all_angry_sun
    1730095541: reach_the_goal_after_defeating_at_least_all_pokey
    1780278293: reach_the_goal_as_superball_mario
    1839897151: reach_the_goal_after_defeating_at_least_all_pom_pom
    1969299694: reach_the_goal_after_defeating_at_least_all_peepa
    2035052211: reach_the_goal_after_defeating_at_least_all_lakitu
    2038503215: reach_the_goal_after_defeating_at_least_all_lemmy
    2048033177: reach_the_goal_after_defeating_at_least_all_lava_bubble
    2076496776: reach_the_goal_while_wearing_a_bullet_bill_mask
    2089161429: reach_the_goal_as_big_mario
    2111528319: reach_the_goal_as_cat_mario
    2131209407: reach_the_goal_after_defeating_at_least_all_goomba_galoomba
    2139645066: reach_the_goal_after_defeating_at_least_all_thwomp
    2259346429: reach_the_goal_after_defeating_at_least_all_iggy
    2549654281: reach_the_goal_while_wearing_a_dry_bones_shell
    2694559007: reach_the_goal_after_defeating_at_least_all_sledge_bro
    2746139466: reach_the_goal_after_defeating_at_least_all_rocky_wrench
    2749601092: reach_the_goal_after_grabbing_at_least_all_50_coin
    2855236681: reach_the_goal_as_flying_squirrel_mario
    3036298571: reach_the_goal_as_buzzy_mario
    3074433106: reach_the_goal_as_builder_mario
    3146932243: reach_the_goal_as_cape_mario
    3174413484: reach_the_goal_after_defeating_at_least_all_wendy
    3206222275: reach_the_goal_while_wearing_a_cannon_box
    3314955857: reach_the_goal_as_link
    3342591980: reach_the_goal_while_you_have_super_star_invincibility
    3346433512: reach_the_goal_after_defeating_at_least_all_goombrat_goombud
    3348058176: reach_the_goal_after_grabbing_at_least_all_10_coin
    3353006607: reach_the_goal_after_defeating_at_least_all_buzzy_beetle
    3392229961: reach_the_goal_after_defeating_at_least_all_bowser_jr
    3437308486: reach_the_goal_after_defeating_at_least_all_koopa_troopa
    3459144213: reach_the_goal_after_defeating_at_least_all_chain_chomp
    3466227835: reach_the_goal_after_defeating_at_least_all_muncher
    3481362698: reach_the_goal_after_defeating_at_least_all_wiggler
    3513732174: reach_the_goal_as_smb2_mario
    3649647177: reach_the_goal_in_a_koopa_clown_car_junior_clown_car
    3725246406: reach_the_goal_as_spiny_mario
    3730243509: reach_the_goal_in_a_koopa_troopa_car
    3748075486: reach_the_goal_after_defeating_at_least_all_piranha_plant_jumping_piranha_plant
    3797704544: reach_the_goal_after_defeating_at_least_all_dry_bones
    3824561269: reach_the_goal_after_defeating_at_least_all_stingby_stingbies
    3833342952: reach_the_goal_after_defeating_at_least_all_piranha_creeper
    3842179831: reach_the_goal_after_defeating_at_least_all_fire_piranha_plant
    3874680510: reach_the_goal_after_breaking_at_least_all_crates
    3974581191: reach_the_goal_after_defeating_at_least_all_ludwig
    3977257962: reach_the_goal_as_super_mario
    4042480826: reach_the_goal_after_defeating_at_least_all_skipsqueak
    4116396131: reach_the_goal_after_grabbing_at_least_all_coin
    4117878280: reach_the_goal_after_defeating_at_least_all_magikoopa
    4122555074: reach_the_goal_after_grabbing_at_least_all_30_coin
    4153835197: reach_the_goal_as_balloon_mario
    4172105156: reach_the_goal_while_wearing_a_red_pow_box
    4209535561: reach_the_goal_while_riding_yoshi
    4269094462: reach_the_goal_after_defeating_at_least_all_spike_top
    4293354249: reach_the_goal_after_defeating_at_least_all_banzai_bill
  autoscroll_speed:
    0: x1
    1: x2
    2: x3
types:
  map:
    seq:
      - id: theme
        type: u1
        enum: theme
        doc: Map theme
      - id: autoscroll_type
        type: u1
        enum: autoscroll_type
        doc: Autoscroll type
      - id: boundary_type
        type: u1
        enum: boundary_type
        doc: Boundary type
      - id: orientation
        type: u1
        enum: orientation
        doc: Orientation
      - id: liquid_end_height
        type: u1
        doc: Liquid end height
      - id: liquid_mode
        type: u1
        enum: liquid_mode
        doc: Liquid mode
      - id: liquid_speed
        type: u1
        enum: liquid_speed
        doc: Liquid speed
      - id: liquid_start_height
        type: u1
        doc: Liquid start height
      - id: boundary_right
        type: s4
        doc: Right boundary
      - id: boundary_top
        type: s4
        doc: Top boundary
      - id: boundary_left
        type: s4
        doc: Left boundary
      - id: boundary_bottom
        type: s4
        doc: Bottom boundary
      - id: unk_flag
        type: s4
        doc: Unknown flag
      - id: object_count
        type: s4
        doc: Object count
      - id: sound_effect_count
        type: s4
        doc: Sound effect count
      - id: snake_block_count
        type: s4
        doc: Snake block count
      - id: clear_pipe_count
        type: s4
        doc: Clear pipe count
      - id: piranha_creeper_count
        type: s4
        doc: Piranha creeper count
      - id: exclamation_mark_block_count
        type: s4
        doc: Exclamation mark block count
      - id: track_block_count
        type: s4
        doc: Track block count
      - id: unk1
        type: s4
      - id: ground_count
        type: s4
        doc: Ground count
      - id: track_count
        type: s4
        doc: Track count
      - id: ice_count
        type: s4
        doc: Ice count
      - id: objects
        type: obj
        repeat: expr
        repeat-expr: 2600
        doc: Objects
      - id: sounds
        type: sound
        repeat: expr
        repeat-expr: 300
        doc: Sound effects
      - id: snakes
        type: snake
        repeat: expr
        repeat-expr: 5
        doc: Snake blocks
      - id: clear_pipes
        type: clear_pipe
        repeat: expr
        repeat-expr: 200
        doc: Clear pipes
      - id: piranha_creepers
        type: piranha_creeper
        repeat: expr
        repeat-expr: 10
        doc: Piranha creepers
      - id: exclamation_blocks
        type: exclamation_block
        repeat: expr
        repeat-expr: 10
        doc: ! Blocks
      - id: track_blocks
        type: track_block
        repeat: expr
        repeat-expr: 10
        doc: Track blocks
      - id: ground
        type: ground
        repeat: expr
        repeat-expr: 4000
        doc: Ground tiles
      - id: tracks
        type: track
        repeat: expr
        repeat-expr: 1500
        doc: Tracks
      - id: icicles
        type: icicle
        repeat: expr
        repeat-expr: 300
        doc: Icicles
      - id: unk2
        size: 0xDBC
    enums:
      theme:
        0: overworld
        1: underground
        2: castle
        3: airship
        4: underwater
        5: ghost_house
        6: snow
        7: desert
        8: sky
        9: forest
      autoscroll_type:
        0: none
        1: slow
        2: normal
        3: fast
        4: custom
      boundary_type:
        0: built_above_line
        1: built_below_line
      orientation:
        0: horizontal
        1: vertical
      liquid_mode:
        0: static
        1: rising_or_falling
        2: rising_and_falling
      liquid_speed:
        0: none
        1: x1
        2: x2
        3: x3
  obj:
    seq:
      - id: x
        type: s4
        doc: X coordinate
      - id: y
        type: s4
        doc: Y coordinate
      - id: unk1
        type: s2
      - id: width
        type: u1
        doc: Width
      - id: height
        type: u1
        doc: Height
      - id: flag
        type: s4
        doc: Flag
      - id: cflag
        type: s4
        doc: CFlag
      - id: ex
        type: s4
        doc: Ex
      - id: id
        type: s2
        enum: obj_id
        doc: ID
      - id: cid
        type: s2
        doc: CID
      - id: lid
        type: s2
        doc: LID
      - id: sid
        type: s2
        doc: SID
    enums:
      obj_id:
        0: goomba
        1: koopa
        2: piranha_flower
        3: hammer_bro
        4: block
        5: question_block
        6: hard_block
        7: ground
        8: coin
        9: pipe
        10: spring
        11: lift
        12: thwomp
        13: bullet_bill_blaster
        14: mushroom_platform
        15: bob_omb
        16: semisolid_platform
        17: bridge
        18: p_switch
        19: pow
        20: super_mushroom
        21: donut_block
        22: cloud
        23: note_block
        24: fire_bar
        25: spiny
        26: goal_ground
        27: goal
        28: buzzy_beetle
        29: hidden_block
        30: lakitu
        31: lakitu_cloud
        32: banzai_bill
        33: one_up
        34: fire_flower
        35: super_star
        36: lava_lift
        37: starting_brick
        38: starting_arrow
        39: magikoopa
        40: spike_top
        41: boo
        42: clown_car
        43: spikes
        44: big_mushroom
        45: shoe_goomba
        46: dry_bones
        47: cannon
        48: blooper
        49: castle_bridge
        50: jumping_machine
        51: skipsqueak
        52: wiggler
        53: fast_conveyor_belt
        54: burner
        55: door
        56: cheep_cheep
        57: muncher
        58: rocky_wrench
        59: track
        60: lava_bubble
        61: chain_chomp
        62: bowser
        63: ice_block
        64: vine
        65: stingby
        66: arrow
        67: one_way
        68: saw
        69: player
        70: big_coin
        71: half_collision_platform
        72: koopa_car
        73: cinobio
        74: spike_ball
        75: stone
        76: twister
        77: boom_boom
        78: pokey
        79: p_block
        80: sprint_platform
        81: smb2_mushroom
        82: donut
        83: skewer
        84: snake_block
        85: track_block
        86: charvaargh
        87: slight_slope
        88: steep_slope
        89: reel_camera
        90: checkpoint_flag
        91: seesaw
        92: red_coin
        93: clear_pipe
        94: conveyor_belt
        95: key
        96: ant_trooper
        97: warp_box
        98: bowser_jr
        99: on_off_block
        100: dotted_line_block
        101: water_marker
        102: monty_mole
        103: fish_bone
        104: angry_sun
        105: swinging_claw
        106: tree
        107: piranha_creeper
        108: blinking_block
        109: sound_effect
        110: spike_block
        111: mechakoopa
        112: crate
        113: mushroom_trampoline
        114: porkupuffer
        115: cinobic
        116: super_hammer
        117: bully
        118: icicle
        119: exclamation_block
        120: lemmy
        121: morton
        122: larry
        123: wendy
        124: iggy
        125: roy
        126: ludwig
        127: cannon_box
        128: propeller_box
        129: goomba_mask
        130: bullet_bill_mask
        131: red_pow_box
        132: on_off_trampoline
  sound:
    seq:
      - id: id
        type: u1
        doc: Sound type
      - id: x
        type: u1
        doc: X position
      - id: y
        type: u1
        doc: Y position
      - id: unk1
        type: u1
  snake:
    seq:
      - id: index
        type: u1
        doc: Snake block index
      - id: node_count
        type: u1
        doc: Snake block node count
      - id: unk1
        type: u2
      - id: nodes
        type: snake_node
        repeat: expr
        repeat-expr: 120
        doc: Snake block nodes
  snake_node:
    seq:
      - id: index
        type: u2
        doc: Snake block node index
      - id: direction
        type: u2
        doc: Snake block node direction
      - id: unk1
        type: u4
  clear_pipe:
    seq:
      - id: index
        type: u1
        doc: Clear pipe index
      - id: node_count
        type: u1
        doc: Clear pipe node count
      - id: unk
        type: u2
      - id: nodes
        type: clear_pipe_node
        repeat: expr
        repeat-expr: 36
        doc: Clear pipe nodes
  clear_pipe_node:
    seq:
      - id: type
        type: u1
        doc: Clear pipe node type
      - id: index
        type: u1
        doc: Clear pipe node index
      - id: x
        type: u1
        doc: Clear pipe node X position
      - id: y
        type: u1
        doc: Clear pipe node Y position
      - id: width
        type: u1
        doc: Clear pipe node width
      - id: height
        type: u1
        doc: Clear pipe node height
      - id: unk1
        type: u1
      - id: direction
        type: u1
        doc: Clear pipe node direction
  piranha_creeper:
    seq:
      - id: unk1
        type: u1
      - id: index
        type: u1
        doc: Piranha creeper index
      - id: node_count
        type: u1
        doc: Piranha creeper node count
      - id: unk2
        type: u1
      - id: nodes
        type: piranha_creeper_node
        repeat: expr
        repeat-expr: 20
        doc: Piranha creeper nodes
  piranha_creeper_node:
    seq:
      - id: unk1
        type: u1
      - id: direction
        type: u1
        doc: Piranha creeper node direction
      - id: unk2
        type: u2
  exclamation_block:
    seq:
      - id: unk1
        type: u1
      - id: index
        type: u1
        doc: ! block index
      - id: node_count
        type: u1
        doc: ! block node count
      - id: unk2
        type: u1
      - id: nodes
        type: exclamation_block_node
        repeat: expr
        repeat-expr: 10
        doc: ! block nodes
  exclamation_block_node:
    seq:
      - id: unk1
        type: u1
      - id: direction
        type: u1
        doc: ! block node direction
      - id: unk2
        type: u2
  track_block:
    seq:
      - id: unk1
        type: u1
      - id: index
        type: u1
        doc: Track block index
      - id: node_count
        type: u1
        doc: Track block node count
      - id: unk2
        type: u1
      - id: nodes
        type: track_block_node
        repeat: expr
        repeat-expr: 10
        doc: Track block nodes
  track_block_node:
    seq:
      - id: unk1
        type: u1
      - id: direction
        type: u1
        doc: Track block node direction
      - id: unk2
        type: u2
  ground:
    seq:
      - id: x
        type: u1
        doc: Ground tile X position
      - id: y
        type: u1
        doc: Ground tile Y position
      - id: id
        type: u1
        doc: Ground tile id
      - id: background_id
        type: u1
        doc: Ground tile background tile
  track:
    seq:
      - id: unk1
        type: u2
      - id: flags
        type: u1
        doc: Track flags
      - id: x
        type: u1
        doc: Track X position
      - id: y
        type: u1
        doc: Track Y position
      - id: type
        type: u1
        doc: Track type
      - id: lid
        type: u2
        doc: Track LID
      - id: unk2
        type: u2
      - id: unk3
        type: u2
  icicle:
    seq:
      - id: x
        type: u1
        doc: Icicle X position
      - id: y
        type: u1
        doc: Icicle Y position
      - id: type
        type: u1
        doc: Icicle type
      - id: unk1
        type: u1