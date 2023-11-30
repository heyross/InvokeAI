from fastapi import APIRouter, Body, HTTPException, Path, Query

from invokeai.app.api.dependencies import ApiDependencies
from invokeai.app.services.shared.pagination import PaginatedResults
from invokeai.app.services.workflow_records.workflow_records_common import (
    Workflow,
    WorkflowNotFoundError,
    WorkflowRecordDTO,
    WorkflowRecordListItemDTO,
    WorkflowWithoutID,
)

workflows_router = APIRouter(prefix="/v1/workflows", tags=["workflows"])


@workflows_router.get(
    "/i/{workflow_id}",
    operation_id="get_workflow",
    responses={
        200: {"model": WorkflowRecordDTO},
    },
)
async def get_workflow(
    workflow_id: str = Path(description="The workflow to get"),
) -> WorkflowRecordDTO:
    """Gets a workflow"""
    try:
        return ApiDependencies.invoker.services.workflow_records.get(workflow_id)
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found")


@workflows_router.patch(
    "/i/{workflow_id}",
    operation_id="update_workflow",
    responses={
        200: {"model": WorkflowRecordDTO},
    },
)
async def update_workflow(
    workflow: Workflow = Body(description="The updated workflow", embed=True),
) -> WorkflowRecordDTO:
    """Updates a workflow"""
    return ApiDependencies.invoker.services.workflow_records.update(workflow=workflow)


@workflows_router.delete(
    "/i/{workflow_id}",
    operation_id="delete_workflow",
)
async def delete_workflow(
    workflow_id: str = Path(description="The workflow to delete"),
) -> None:
    """Deletes a workflow"""
    ApiDependencies.invoker.services.workflow_records.delete(workflow_id)


@workflows_router.post(
    "/",
    operation_id="create_workflow",
    responses={
        200: {"model": WorkflowRecordDTO},
    },
)
async def create_workflow(
    workflow: WorkflowWithoutID = Body(description="The workflow to create", embed=True),
) -> WorkflowRecordDTO:
    """Creates a workflow"""
    return ApiDependencies.invoker.services.workflow_records.create(workflow)


@workflows_router.get(
    "/",
    operation_id="list_workflows",
    responses={
        200: {"model": PaginatedResults[WorkflowRecordListItemDTO]},
    },
)
async def list_workflows(
    page: int = Query(default=0, description="The page to get"),
    per_page: int = Query(default=10, description="The number of workflows per page"),
) -> PaginatedResults[WorkflowRecordListItemDTO]:
    """Gets a page of workflows"""
    return ApiDependencies.invoker.services.workflow_records.get_many(page=page, per_page=per_page)
