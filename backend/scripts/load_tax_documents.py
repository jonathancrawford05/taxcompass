"""
Document Ingestion Script
Loads tax documents into Qdrant vector store for RAG
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.rag.vectorstore import get_vector_store_manager
from app.rag.embeddings import get_embeddings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample CRA tax residency content
# In production, these would be loaded from actual PDF documents
SAMPLE_DOCUMENTS = [
    {
        "content": """
CANADA REVENUE AGENCY - RESIDENCY DETERMINATION

Determining Your Residency Status

You are generally considered a resident of Canada for income tax purposes if you:
- Normally, customarily, or routinely live in Canada
- Have significant residential ties to Canada

Significant residential ties include:
- A home in Canada
- A spouse or common-law partner in Canada
- Dependents in Canada

Secondary residential ties include:
- Personal property in Canada (furniture, clothing, automobiles)
- Social ties in Canada
- Economic ties in Canada (employment, business, bank accounts)
- A Canadian driver's license
- A Canadian passport
- Health insurance with a Canadian province or territory
        """,
        "metadata": {
            "source": "CRA Folio S5-F1-C1",
            "country": "CA",
            "topic": "residency_determination",
            "section": "significant_ties"
        }
    },
    {
        "content": """
CANADA REVENUE AGENCY - DEEMED RESIDENTS

Deemed Residents of Canada

You are a deemed resident of Canada if you were not a factual resident of Canada and one of the following applies:
- You stayed in Canada for 183 days or more in the tax year
- You are a member of the Canadian Forces
- You are an officer or servant of Canada or a province
- You performed services in a country other than Canada under a prescribed international development assistance program

If you are a deemed resident, you are subject to Canadian income tax on your worldwide income for the entire year.
        """,
        "metadata": {
            "source": "CRA Folio S5-F1-C1",
            "country": "CA",
            "topic": "residency_determination",
            "section": "deemed_resident"
        }
    },
    {
        "content": """
CANADA REVENUE AGENCY - NON-RESIDENTS

Becoming a Non-Resident of Canada

You become a non-resident of Canada when you sever your residential ties with Canada. This generally happens when you:
- Sell or rent your home in Canada
- Your spouse or common-law partner and dependents leave Canada with you
- You give up memberships in Canadian organizations
- You close Canadian bank accounts, credit cards, and investment accounts

Important: You may still be considered a factual resident if you maintain significant residential ties to Canada, even if you live abroad.

Tax Obligations for Non-Residents:
- File a departure tax return (deemed disposition of property)
- File NR73 form to determine residency status
- May need to file Part XIII tax returns for Canadian-source income
        """,
        "metadata": {
            "source": "CRA Folio S5-F1-C1",
            "country": "CA",
            "topic": "residency_determination",
            "section": "non_resident"
        }
    },
    {
        "content": """
CANADA REVENUE AGENCY - DEPARTURE TAX

Departure Tax (Deemed Disposition)

When you emigrate from Canada, you are deemed to have disposed of certain types of property at fair market value and to have immediately reacquired them at the same value. This is commonly called the departure tax or emigration tax.

Property Subject to Deemed Disposition:
- Shares of corporations
- Units of mutual fund trusts
- Interests in partnerships
- Capital property (with some exceptions)
- RRSP and RRIF accounts (special rules apply)

Exemptions:
- Real property situated in Canada (taxed when actually sold)
- Canadian business property
- Pension plans and RRSPs (taxed when withdrawn)

You must report any capital gains or losses from the deemed disposition on your tax return for the year of emigration.
        """,
        "metadata": {
            "source": "CRA Guide T4056",
            "country": "CA",
            "topic": "departure_tax",
            "section": "deemed_disposition"
        }
    },
    {
        "content": """
CANADA REVENUE AGENCY - RENTAL PROPERTY AND NON-RESIDENTS

Rental Property - Non-Resident Considerations

If you own rental property in Canada and become a non-resident:

Option 1: Section 216 Election
- File a Canadian tax return to report net rental income
- Claim expenses against rental income
- Pay tax at graduated rates

Option 2: Non-Resident Withholding Tax
- Tenant or property manager withholds 25% of gross rental income
- Remit to CRA monthly
- No deduction for expenses

File NR6 form to reduce withholding tax if you elect under Section 216.

Important: Even as a non-resident, you must continue to report Canadian rental income and may be subject to Canadian tax obligations.
        """,
        "metadata": {
            "source": "CRA Guide T4144",
            "country": "CA",
            "topic": "rental_property",
            "section": "non_resident_rental"
        }
    },
    {
        "content": """
UAE TAX RESIDENCY

United Arab Emirates - Tax Residency Rules

The UAE introduced corporate tax in 2023, but individuals are generally not subject to personal income tax.

Corporate Tax Residence:
An entity is considered a UAE tax resident if:
- It is incorporated or established in the UAE
- It is effectively managed and controlled in the UAE

Individual Tax Residence:
While there is no personal income tax in the UAE, determining tax residency is important for:
- Tax treaty benefits
- Avoiding dual residency with other countries
- Demonstrating tax residency to other jurisdictions

Factors Considered:
- Physical presence in the UAE
- Residence visa
- UAE identification documents
- Economic and social ties to the UAE
- Family location

Note: Many countries will not recognize UAE tax residency unless you spend substantial time (typically 183+ days) in the UAE.
        """,
        "metadata": {
            "source": "UAE Federal Tax Authority",
            "country": "AE",
            "topic": "residency_determination",
            "section": "uae_residency"
        }
    },
    {
        "content": """
CANADA-UAE TAX TREATY

Tax Treaty Between Canada and United Arab Emirates

Canada and the UAE have a tax treaty to prevent double taxation and fiscal evasion.

Tie-Breaker Rules (Article 4):
If you are considered a resident of both Canada and the UAE, your residence is determined by:
1. Permanent home available - where you have a permanent home
2. Centre of vital interests - personal and economic relations are closer
3. Habitual abode - where you habitually live
4. Nationality - which country you are a national of
5. Mutual agreement - tax authorities decide

Key Treaty Benefits:
- Reduced withholding tax rates on dividends, interest, and royalties
- Exemption from tax in one country for certain types of income
- Prevention of double taxation through foreign tax credits

Important for Canadians Moving to UAE:
- May still be considered a Canadian tax resident under the treaty
- Must sever residential ties to avoid dual residency
- Treaty does not override domestic residency rules
        """,
        "metadata": {
            "source": "Canada-UAE Tax Treaty",
            "country": "CA",
            "topic": "tax_treaty",
            "section": "treaty_provisions"
        }
    },
    {
        "content": """
FORM NR73 - DETERMINATION OF RESIDENCY STATUS

Form NR73: Determination of Residency Status (Leaving Canada)

You should file Form NR73 if you:
- Want to establish the date you became a non-resident
- Need confirmation of your residency status
- Are leaving Canada permanently or for an extended period

Information Required on NR73:
- Details of your departure from Canada
- Information about residential ties you maintained or severed
- Details about property, investments, and bank accounts
- Information about your spouse and dependents
- Your intended period of absence from Canada

Processing Time:
- Generally 4-6 months
- CRA will issue a letter confirming your residency status
- This letter can be used to demonstrate non-residency to financial institutions

Important: Filing NR73 is optional but highly recommended to establish your non-resident status for tax purposes.
        """,
        "metadata": {
            "source": "CRA Form NR73",
            "country": "CA",
            "topic": "forms",
            "section": "nr73"
        }
    }
]


def load_sample_documents():
    """Load sample tax documents into vector store"""

    logger.info("Starting document ingestion...")

    # Get vector store manager
    vs_manager = get_vector_store_manager()

    # Extract texts and metadatas
    texts = [doc["content"].strip() for doc in SAMPLE_DOCUMENTS]
    metadatas = [doc["metadata"] for doc in SAMPLE_DOCUMENTS]

    # Add documents to vector store
    logger.info(f"Adding {len(texts)} documents to vector store...")

    try:
        ids = vs_manager.add_documents(texts=texts, metadatas=metadatas)
        logger.info(f"✓ Successfully added {len(ids)} documents")

        # Verify collection
        info = vs_manager.get_collection_info()
        logger.info(f"✓ Collection '{info['name']}' now contains {info['points_count']} documents")

        # Test search
        logger.info("\nTesting search functionality...")
        test_query = "What are significant residential ties in Canada?"
        results = vs_manager.search(query=test_query, k=3)

        logger.info(f"\nSearch results for: '{test_query}'")
        for i, result in enumerate(results, 1):
            logger.info(f"\n{i}. Source: {result['metadata'].get('source', 'Unknown')}")
            logger.info(f"   Score: {result['score']:.4f}")
            logger.info(f"   Preview: {result['content'][:150]}...")

        logger.info("\n" + "="*80)
        logger.info("✓ Document ingestion completed successfully!")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"✗ Failed to add documents: {str(e)}")
        raise


if __name__ == "__main__":
    load_sample_documents()
