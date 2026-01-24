"""Markdown templates for activity files."""

ACTIVITY_TEMPLATE = """# {title}

**Status**: {status}
**Criado em**: {created_at}
**Última Atualização**: {updated_at}

## Descrição

{description}

## Declaração do Problema

{problem}

## Stakeholders

{stakeholders}

## Restrições e Cronograma

{constraints}

## Sistema/Produto Afetado

{affected_system}

## Metadados

{metadata}
"""

LOG_TEMPLATE = """# Log da Atividade: {title}

Todas as entradas são registradas aqui em ordem cronológica.

---

"""

CANVAS_TEMPLATE = """# Business Case Canvas: {title}

## Problema

**Qual é o problema?**
{problem_statement}

**Quem tem o problema?**
{problem_owner}

**Por que é importante?**
{problem_importance}

## Solução

**Solução Proposta:**
{proposed_solution}

**Como se relaciona com o problema?**
{solution_relation}

## Recursos

**Recursos Tangíveis:**
{tangible_resources}

**Recursos Intangíveis:**
{intangible_resources}

**Dependências Internas:**
{internal_dependencies}

**Dependências Externas:**
{external_dependencies}

## Benefícios

**Propósito (Por que estamos fazendo isso?):**
{purpose}

**Objetivos:**
{goals}

**Benefícios Financeiros:**
{financial_benefits}

**Benefícios Não-Financeiros:**
{non_financial_benefits}

## Escopo

**Dentro do Escopo:**
{in_scope}

**Fora do Escopo:**
{out_of_scope}

**Cronograma:**
{timeline}

**Recursos Disponíveis:**
{resources_available}

**Relevância Estratégica:**
{strategic_relevance}

## Riscos

{risks}

## Stakeholders

{stakeholders}

## Análise de Complexidade

**Esforço de Especificação/Documentação:**
{specification_effort}

**Esforço de Desenvolvimento:**
{development_effort}

**Esforço de Testes:**
{testing_effort}

## Plano de Comunicação

**Materiais:**
{materials}

**Vídeos:**
{videos}

**Treinamento:**
{training}

## Custos

**Fontes de Custo:**
{cost_sources}

**Orçamento:**
{budget}

**Custo Total ao Longo do Tempo:**
{total_cost_over_time}

## Métricas

**Métricas de Sucesso:**
{success_metrics}

**Métricas de Benefício:**
{benefit_metrics}

---

## Informações Faltantes

{missing_info}

## Perguntas Sugeridas para Completar o Canvas

{suggested_questions}
"""

JIRA_EXPORT_TEMPLATE = """# Exportação Jira: {title}

Gerado em: {timestamp}

---

"""
