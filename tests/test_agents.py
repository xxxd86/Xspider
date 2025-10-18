from agents.wechat import WeChatAgent


def test_wechat_agent_fetch_returns_records():
    agent = WeChatAgent()
    records = agent.fetch("Acme", ["innovation", "Acme"])
    assert records
    assert all(record["company"] == "Acme" for record in records)
