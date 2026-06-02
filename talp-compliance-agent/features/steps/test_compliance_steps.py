"""
BDD Steps para testes de compliance
"""

from behave import given, when, then


@given("the compliance agent is running")
def step_agent_running(context):
    """Verificar que o agente está rodando."""
    pass


@when("I check the health endpoint")
def step_check_health(context):
    """Fazer requisição ao health endpoint."""
    pass


@then("the agent should respond with status healthy")
def step_verify_health(context):
    """Verificar resposta do health endpoint."""
    pass
