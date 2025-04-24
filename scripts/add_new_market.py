def add_new_market(market_info, is_testnet=False):
    data = {"values": {}, "invokes": {}, "oracle": {}}
    settings = {}
    invokes = {"invoke": {}}
    oracle = {"invoke": {}}

    prefix = "perps" + market_info["ticker"].capitalize()
    settings[f"{prefix}FeedId"] = {"defaultValue": market_info["feed_id"]}
    settings[f"{prefix}MarketId"] = {"defaultValue": market_info["market_id"]}
    settings[f"{prefix}SkewScale"] = {
        "defaultValue": f'<%= String({int(market_info["skew_scale"]):_}) %>'
    }
    settings[f"{prefix}MaxFundingVelocity"] = {"defaultValue": "24"}
    settings[f"{prefix}MakerFeeRatio"] = {"defaultValue": "0.0005"}
    settings[f"{prefix}TakerFeeRatio"] = {"defaultValue": "0.0008"}
    settings[f"{prefix}LimitOrderMakerFeeRatio"] = {"defaultValue": "0.0001"}
    settings[f"{prefix}LimitOrderTakerFeeRatio"] = {"defaultValue": "0.0002"}
    settings[f"{prefix}MaxMarketSize"] = {
        "defaultValue": f'<%= String({market_info["max_market_size"]:.2f}) %>'
    }
    settings[f"{prefix}MaxMarketValue"] = {
        "defaultValue": f'<%= String({int(market_info["max_market_value"]):_}) %>'
    }
    settings[f"{prefix}InitialMarginRatio"] = {
        "defaultValue": str(market_info["initial_margin_ratio"])
    }
    settings[f"{prefix}MaintenanceMarginScalar"] = {
        "defaultValue": str(market_info["maintenance_margin_scalar"])
    }
    settings[f"{prefix}MinimumInitialMarginRatio"] = {
        "defaultValue": str(market_info["inverse_leverage"])
    }
    settings[f"{prefix}FlagRewardRatioD18"] = {"defaultValue": "0.0003"}
    settings[f"{prefix}MaxLiquidationLimitAccumulationMultiplier"] = {
        "defaultValue": "1.5"
    }
    settings[f"{prefix}MaxSecondsInLiquidationWindow"] = {"defaultValue": "30"}
    settings[f"{prefix}MinimumPositionMargin"] = {"defaultValue": "50"}
    settings[f"{prefix}LockedOiRatio"] = {"defaultValue": "0.5"}
    settings[f"{prefix}SynthMaxCollateralAmount"] = {
        "defaultValue": "<%= MaxUint256 %>"
    }
    settings[f"{prefix}MaxLiquidationPd"] = {"defaultValue": "0.0005"}
    settings[f"{prefix}EndorsedLiquidator"] = {
        "defaultValue": "0x38D4200767628f4197C5d5FdDA24927C28dDadeF"
    }
    settings["commitmentPriceDelay"] = {"defaultValue": "2"}
    settings["bigCapSettlementDelay"] = {"defaultValue": "2"}

    invokes["include"] = [
        f"../../oracles/pyth-{market_info['ticker']}.toml",
        f"../../markets/common/bigcap-settings.toml",
    ]
    invokes["setting"] = {
        f"{prefix}MarketId": {},
        f"{prefix}SkewScale": {},
        f"{prefix}MaxFundingVelocity": {},
        f"{prefix}MakerFeeRatio": {},
        f"{prefix}TakerFeeRatio": {},
        f"{prefix}MaxMarketSize": {},
        f"{prefix}InitialMarginRatio": {},
        f"{prefix}MaintenanceMarginScalar": {},
        f"{prefix}MinimumInitialMarginRatio": {},
        f"{prefix}FlagRewardRatioD18": {},
        f"{prefix}MaxLiquidationLimitAccumulationMultiplier": {},
        f"{prefix}MaxSecondsInLiquidationWindow": {},
        f"{prefix}MinimumPositionMargin": {},
        f"{prefix}LockedOiRatio": {},
        f"{prefix}SynthMaxCollateralAmount": {},
        f"{prefix}MaxLiquidationPd": {},
        f"{prefix}EndorsedLiquidator": {},
    }

    invoke = {}
    invoke[f"create{prefix}Market"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "createMarket",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            market_info["name"],
            market_info["ticker"].upper(),
        ],
        "depends": ["provision.system", "provision.perpsFactory"],
    }
    invoke[f"set{prefix}Price"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "updatePriceData",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= extras.{prefix}_oracle_id %>",
            "<%= settings.bigCapStrictStalenessTolerance %>",
        ],
        "depends": [f"invoke.create{prefix}Market"],
    }
    invoke[f"add{prefix}SettlementStrategy"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "addSettlementStrategy",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            {
                "strategyType": "0",
                "settlementDelay": "0",
                "settlementWindowDuration": "1",
                "priceVerificationContract": "0x0000000000000000000000000000000000000000",
                "feedId": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "settlementReward": "0",
                "disabled": False,
                "commitmentPriceDelay": "0",
            },
        ],
        "extra": {
            f"{prefix}_pyth_settlement_strategy": {
                "event": "SettlementStrategyAdded",
                "arg": 2,
            }
        },
        "depends": [f"invoke.create{prefix}Market"],
    }
    invoke[f"set{prefix}SettlementStrategy"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "setSettlementStrategy",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= extras.{prefix}_pyth_settlement_strategy %>",
            {
                "strategyType": "0",
                "settlementDelay": "<%= settings.bigCapSettlementDelay %>",
                "settlementWindowDuration": "<%= settings.bigCapSettlementWindowDuration %>",
                "priceVerificationContract": "<%= imports.pyth_erc7412_wrapper.contracts.PythERC7412Wrapper.address %>",
                "feedId": f"<%= settings.{prefix}FeedId %>",
                "settlementReward": "<%= parseEther(settings.settlementReward) %>",
                "disabled": False,
                "commitmentPriceDelay": "2",
            },
        ],
        "depends": [
            "provision.perpsFactory",
            f"setting.{prefix}MarketId",
            f"invoke.add{prefix}SettlementStrategy",
            "provision.pyth_erc7412_wrapper",
            "setting.bigCapSettlementDelay",
            "setting.bigCapSettlementWindowDuration",
            f"setting.{prefix}FeedId",
            "setting.settlementReward",
        ],
    }
    invoke[f"set{prefix}FundingParameters"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "setFundingParameters",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= parseEther(settings.{prefix}SkewScale) %>",
            f"<%= parseEther(settings.{prefix}MaxFundingVelocity) %>",
        ],
        "depends": [f"invoke.create{prefix}Market"],
    }
    invoke[f"set{prefix}OrderFees"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "setOrderFees",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= parseEther(settings.{prefix}MakerFeeRatio) %>",
            f"<%= parseEther(settings.{prefix}TakerFeeRatio) %>",
        ],
        "depends": [f"invoke.create{prefix}Market"],
    }
    invoke[f"set{prefix}MaxMarketSize"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "setMaxMarketSize",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= parseEther(settings.{prefix}MaxMarketSize) %>",
        ],
        "depends": [f"invoke.create{prefix}Market"],
    }
    invoke[f"set{prefix}MaxMarketValue"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "setMaxMarketValue",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= parseEther(settings.{prefix}MaxMarketValue) %>",
        ],
        "depends": [f"invoke.create{prefix}Market"],
    }
    invoke[f"set{prefix}MaxLiquidationParameters"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "setMaxLiquidationParameters",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= parseEther(settings.{prefix}MaxLiquidationLimitAccumulationMultiplier) %>",
            f"<%= settings.{prefix}MaxSecondsInLiquidationWindow %>",
            f"<%= parseEther(settings.{prefix}MaxLiquidationPd) %>",
            f"<%= settings.{prefix}EndorsedLiquidator %>",
        ],
        "depends": [f"invoke.create{prefix}Market"],
    }
    invoke[f"set{prefix}LiquidationParameters"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "setLiquidationParameters",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= parseEther(settings.{prefix}InitialMarginRatio) %>",
            f"<%= parseEther(settings.{prefix}MinimumInitialMarginRatio) %>",
            f"<%= parseEther(settings.{prefix}MaintenanceMarginScalar) %>",
            f"<%= parseEther(settings.{prefix}FlagRewardRatioD18) %>",
            f"<%= parseEther(settings.{prefix}MinimumPositionMargin) %>",
        ],
        "depends": [f"invoke.create{prefix}Market"],
    }
    invoke[f"set{prefix}LockedOiRatio"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "setLockedOiRatio",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= parseEther(settings.{prefix}LockedOiRatio) %>",
        ],
        "depends": [f"invoke.create{prefix}Market"],
    }

    invoke[f"set{prefix}LimitOrderFees"] = {
        "target": ["perpsFactory.PerpsMarketProxy"],
        "fromCall": {"func": "owner"},
        "func": "setLimitOrderFees",
        "args": [
            f"<%= settings.{prefix}MarketId %>",
            f"<%= parseEther(settings.{prefix}LimitOrderMakerFeeRatio) %>",
            f"<%= parseEther(settings.{prefix}LimitOrderTakerFeeRatio) %>",
        ],
        "depends": [f"invoke.create{prefix}Market"],
    }

    oracle["invoke"] = {
        f"register{prefix}PythOracleNode": {
            "target": ["system.oracle_manager.Proxy"],
            "func": "registerNode",
            "args": [
                5,  # 5 = pyth aggregator type
                f"<%= defaultAbiCoder.encode(['address', 'bytes32', 'bool'], [settings.pyth_price_verification_address, settings.{prefix}FeedId, false]) %>",
                [],
            ],
            "depends": ["provision.system"],
            "extra": {
                f"{prefix}_pyth_oracle_id": {
                    "event": "NodeRegistered",
                    "arg": 0,
                }
            },
        },
        f"register{prefix}LookupOracleNode": {
            "target": ["system.oracle_manager.Proxy"],
            "func": "registerNode",
            "args": [
                9,
                f"<%= defaultAbiCoder.encode(['address', 'bytes32', 'uint256'], [imports.pyth_erc7412_wrapper.contracts.PythERC7412Wrapper.address, settings.{prefix}FeedId, settings.bigCapDefaultStalenessTolerance]) %>",
                [],
            ],
            "depends": ["provision.system"],
            "extra": {
                f"{prefix}_lookup_oracle_id": {
                    "event": "NodeRegistered",
                    "arg": 0,
                }
            },
        },
        f"register{prefix}OracleNode": {
            "target": ["system.oracle_manager.Proxy"],
            "func": "registerNode",
            "args": [
                7,
                f"<%= defaultAbiCoder.encode(['uint256'], [settings.bigCapDefaultStalenessTolerance]) %>",
                [
                    f"<%= extras.{prefix}_pyth_oracle_id %>",
                    f"<%= extras.{prefix}_lookup_oracle_id %>",
                ],
            ],
            "depends": ["provision.system"],
            "extra": {
                f"{prefix}_oracle_id": {
                    "event": "NodeRegistered",
                    "arg": 0,
                }
            },
        },
    }

    data["values"]["setting"] = settings
    data["invokes"]["include"] = invokes["include"]
    data["invokes"]["setting"] = invokes["setting"]
    data["invokes"]["invoke"] = invoke
    data["oracle"] = oracle
    return data
