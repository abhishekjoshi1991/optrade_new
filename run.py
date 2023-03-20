from tradeapp import app, sched
import os
from tradeapp.schedulers.scheduler import option_chain_scheduler


port = "7010"
debug = True


# app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)  

if __name__ == "__main__":
    sched.add_job(id="job1", func=option_chain_scheduler, trigger='interval', minutes=5)
    # sched.start()
    app.run(port=port, debug=debug, use_reloader=True)
    