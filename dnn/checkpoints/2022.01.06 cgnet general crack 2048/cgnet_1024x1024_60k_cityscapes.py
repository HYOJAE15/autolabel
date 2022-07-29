norm_cfg = dict(type='SyncBN', eps=0.001, requires_grad=True)
model = dict(
    type='EncoderDecoder',
    backbone=dict(
        type='CGNet',
        norm_cfg=dict(type='SyncBN', eps=0.001, requires_grad=True),
        in_channels=3,
        num_channels=(32, 64, 128),
        num_blocks=(3, 21),
        dilations=(2, 4),
        reductions=(8, 16)),
    decode_head=dict(
        type='FCNHead',
        in_channels=256,
        in_index=2,
        channels=256,
        num_convs=0,
        concat_input=False,
        dropout_ratio=0,
        num_classes=2,
        norm_cfg=dict(type='SyncBN', eps=0.001, requires_grad=True),
        loss_decode=dict(
            type='CrossEntropyLoss',
            use_sigmoid=False,
            loss_weight=1.0,
            class_weight=[2.5959933, 6.7415504])),
    train_cfg=dict(sampler=None),
    test_cfg=dict(mode='whole'))
log_config = dict(
    interval=50, hooks=[dict(type='TextLoggerHook', by_epoch=False)])
dist_params = dict(backend='nccl')
log_level = 'INFO'
load_from = None
resume_from = None
workflow = [('train', 1)]
cudnn_benchmark = True
optimizer = dict(type='Adam', lr=0.001, eps=1e-08, weight_decay=0.0005)
optimizer_config = dict()
lr_config = dict(policy='poly', power=0.9, min_lr=0.0001, by_epoch=False)
total_iters = 60000
checkpoint_config = dict(by_epoch=False, interval=4000)
evaluation = dict(interval=4000, metric='mIoU')
dataset_type = 'EfflorescenceCityscapesDataset'
data_root = '/home/user/UOS-SSaS Dropbox/05. Data/02. Training&Test/102. Autolabel-train/02. efflorescence/raw'
img_norm_cfg = dict(
    mean=[72.39239876, 82.90891754, 73.15835921], std=[1, 1, 1], to_rgb=True)
crop_size = (1024, 1024)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations'),
    dict(type='Resize', img_scale=(1024, 2048), ratio_range=(0.5, 2.0)),
    dict(type='RandomCrop', crop_size=(1024, 1024), cat_max_ratio=0.75),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='PhotoMetricDistortion'),
    dict(
        type='Normalize',
        mean=[72.39239876, 82.90891754, 73.15835921],
        std=[1, 1, 1],
        to_rgb=True),
    dict(type='Pad', size=(1024, 1024), pad_val=0, seg_pad_val=255),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg'])
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(1024, 1024),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(
                type='Normalize',
                mean=[72.39239876, 82.90891754, 73.15835921],
                std=[1, 1, 1],
                to_rgb=True),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img'])
        ])
]
data = dict(
    samples_per_gpu=8,
    workers_per_gpu=4,
    train=dict(
        type='EfflorescenceCityscapesDataset',
        data_root=
        '/home/user/UOS-SSaS Dropbox/05. Data/02. Training&Test/102. Autolabel-train/02. efflorescence/raw',
        img_dir='leftImg8bit/train',
        ann_dir='gtFine/train',
        pipeline=[
            dict(type='LoadImageFromFile'),
            dict(type='LoadAnnotations'),
            dict(
                type='Resize', img_scale=(1024, 2048), ratio_range=(0.5, 2.0)),
            dict(
                type='RandomCrop', crop_size=(1024, 1024), cat_max_ratio=0.75),
            dict(type='RandomFlip', flip_ratio=0.5),
            dict(type='PhotoMetricDistortion'),
            dict(
                type='Normalize',
                mean=[72.39239876, 82.90891754, 73.15835921],
                std=[1, 1, 1],
                to_rgb=True),
            dict(type='Pad', size=(1024, 1024), pad_val=0, seg_pad_val=255),
            dict(type='DefaultFormatBundle'),
            dict(type='Collect', keys=['img', 'gt_semantic_seg'])
        ]),
    val=dict(
        type='EfflorescenceCityscapesDataset',
        data_root=
        '/home/user/UOS-SSaS Dropbox/05. Data/02. Training&Test/102. Autolabel-train/02. efflorescence/raw',
        img_dir='leftImg8bit/val',
        ann_dir='gtFine/val',
        pipeline=[
            dict(type='LoadImageFromFile'),
            dict(
                type='MultiScaleFlipAug',
                img_scale=(1024, 1024),
                flip=False,
                transforms=[
                    dict(type='Resize', keep_ratio=True),
                    dict(type='RandomFlip'),
                    dict(
                        type='Normalize',
                        mean=[72.39239876, 82.90891754, 73.15835921],
                        std=[1, 1, 1],
                        to_rgb=True),
                    dict(type='ImageToTensor', keys=['img']),
                    dict(type='Collect', keys=['img'])
                ])
        ]),
    test=dict(
        type='EfflorescenceCityscapesDataset',
        data_root=
        '/home/user/UOS-SSaS Dropbox/05. Data/02. Training&Test/102. Autolabel-train/02. efflorescence/raw',
        img_dir='leftImg8bit/test',
        ann_dir='gtFine/test',
        pipeline=[
            dict(type='LoadImageFromFile'),
            dict(
                type='MultiScaleFlipAug',
                img_scale=(1024, 1024),
                flip=False,
                transforms=[
                    dict(type='Resize', keep_ratio=True),
                    dict(type='RandomFlip'),
                    dict(
                        type='Normalize',
                        mean=[72.39239876, 82.90891754, 73.15835921],
                        std=[1, 1, 1],
                        to_rgb=True),
                    dict(type='ImageToTensor', keys=['img']),
                    dict(type='Collect', keys=['img'])
                ])
        ]))
work_dir = './work_dirs/cgnet_1024x1024_60k_cityscapes'
gpu_ids = range(0, 4)
auto_resume = False
