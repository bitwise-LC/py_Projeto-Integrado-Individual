# Leitura dos dados para a entrega individual

**Fontes:** IBGE, Censo Demográfico 2022, [SIDRA 9543](https://sidra.ibge.gov.br/tabela/9543) (taxa de alfabetização de pessoas de 15 anos ou mais) e [SIDRA 10333](https://sidra.ibge.gov.br/tabela/10333) (pessoas ocupadas de 10 anos ou mais que trabalhavam fora do domicílio, por instrução e tempo habitual de ida ao trabalho). Consulta à API em 06/11/2026. Arquivos preservados em `dados/`.

## Alfabetização por UF

Nas 27 UFs, a média simples das taxas foi **91,19%** e a mediana, **93,08%**. O primeiro quartil foi **86,39%** e o terceiro, **94,56%**, com IQR de **8,17 pontos percentuais**. O desvio padrão amostral foi **4,90 pontos percentuais**; a amplitude, **14,99 pontos**. A menor taxa foi em **Alagoas (82,34%)** e a maior em **Santa Catarina (97,33%)**. Pela regra de 1,5 × IQR, não houve UF outlier nesse conjunto.

A média abaixo da mediana mostra que taxas mais baixas puxam a média das UFs para baixo. A média simples das 27 taxas **não é a taxa de alfabetização do Brasil**: cada UF entra com o mesmo peso, embora as populações sejam diferentes.

## Escolaridade e viagem longa

Na tabela 10333, a parcela de pessoas ocupadas com **tempo habitual de ida ao trabalho acima de uma hora** foi:

| Nível de instrução | Pessoas no grupo | Acima de 1 hora | Parcela |
| --- | ---: | ---: | ---: |
| Sem instrução e fundamental incompleto | 14.324.061 | 1.854.277 | 12,95% |
| Fundamental completo e médio incompleto | 11.095.733 | 1.427.946 | 12,87% |
| Médio completo e superior incompleto | 29.551.926 | 3.677.951 | 12,45% |
| Superior completo | 16.324.459 | 1.704.984 | 10,44% |

Há uma associação descritiva: a parcela com viagem longa cai de **12,95%** no grupo de menor instrução para **10,44%** no grupo de superior completo, diferença de **2,51 pontos percentuais**. Os dados não demonstram que a escolaridade causa o tempo de viagem. Distância da residência, transporte disponível, localização dos empregos e renda podem influenciar o resultado. A taxa de alfabetização e a tabela de deslocamento também se referem a populações diferentes; não há correlação individual identificável entre as duas bases agregadas.

## Fala sugerida na roda de conversa

> “No Censo 2022, a taxa de alfabetização variou quase 15 pontos entre as UFs. Entre os trabalhadores que estudamos, viagens de mais de uma hora aparecem em 12,95% do grupo com menor instrução e em 10,44% do grupo com superior completo. Isso sugere investigar onde educação, emprego e transporte se sobrepõem. Para decidir onde investir, precisamos olhar os territórios e a oferta de transporte, sem tratar essa associação como causa comprovada.”
