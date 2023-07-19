from pyzeebe import ZeebeClient, create_insecure_channel, ZeebeWorker
from pyzeebe import Job
import asyncio
import nest_asyncio
nest_asyncio.apply()

channel = create_insecure_channel()
client = ZeebeClient(channel)
worker = ZeebeWorker(channel)


async def my_exception_handler(exception: Exception, job: Job) -> None:
    print(exception)
    await job.set_failure_status(message=str(exception))


@worker.task(task_type="io.camunda.zeebe:userTask", exception_handler=my_exception_handler)
async def my_task(name: str, approver: str, job: Job, status: int):
    print("Report Name: ", name)
    print("Approver: ", approver)
    # print(dir(job))
    print("Job Status: ", job.status)
    print("Task Worker: ", job.worker)
    print("BPMN Process ID: ", job.bpmn_process_id)
    print("Custom Headers: ", job.custom_headers)
    print("DeadLine: ", job.deadline)
    print("Element ID: ", job.element_id)
    print("Element Instance Key: ", job.element_instance_key)
    print("Key: ", job.key)
    print("Process Definition Key: ", job.process_definition_key)
    print("Process Definition Version: ", job.process_definition_version)
    print("Process Instance Key: ", job.process_instance_key)
    print("Retries: ", job.retries)
    print("Status: ", job.status)
    print("Type: ", job.type)
    print("Variables: ", job.variables)
    print("Worker: ", job.worker)
    print("Zeebee Adapter: ", job.zeebe_adapter)
    if job.status == 1: # this means report is approved
        return {"approved": True}

loop = asyncio.get_event_loop()
loop.run_until_complete(worker.work())
