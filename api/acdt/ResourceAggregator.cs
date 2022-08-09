using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace acdt
{
    //Takes raw resources and aggregates then into a new model
    public static class ResourceAggregator
    {
        //Aggregate the Resources into a Location, rg based grouping.
        public static Dictionary<string, int> GroupCountByLocation(ResourceGroups groups)
        {
            Dictionary<string, int> locationGroupCount = new Dictionary<string, int>();
            int total = 0;
            foreach (ResourceGroup group in groups)
            {
                total++;
                if (!locationGroupCount.ContainsKey(group.Location))
                {
                    locationGroupCount[group.Location] = 1;
                } else
                {
                    locationGroupCount[group.Location]++;
                }
            }
            locationGroupCount["Total"] = total;

            return locationGroupCount;
        }

        //Aggregate the Resources into a Location, rg based grouping.
        public static Dictionary<string, int> ResourceCountByLocation(Resources groups)
        {
            Dictionary<string, int> locationGroupCount = new Dictionary<string, int>();
            int total = 0;
            foreach (Resource group in groups)
            {
                total++;
                if (!locationGroupCount.ContainsKey(group.Location))
                {
                    locationGroupCount[group.Location] = 1;
                }
                else
                {
                    locationGroupCount[group.Location]++;
                }
            }
            locationGroupCount["Total"] = total;

            return locationGroupCount;
        }

        //Aggregate the Resources into a Location, rg based grouping.
        public static Dictionary<string, int> CountByType(Resources resources)
        {
            Dictionary<string, int> typeGroupCount = new Dictionary<string, int>();
            int total = 0;

            foreach (Resource res in resources)
            {
                total++;
                if (!typeGroupCount.ContainsKey(res.Type))
                {
                    typeGroupCount[res.Type] = 1;
                }
                else
                {
                    typeGroupCount[res.Type]++;
                }
            }

            typeGroupCount["Total"] = total;

            return typeGroupCount;
        }

        //Aggregate the Resources into a Location, rg based grouping.
        public static Dictionary<string, int> CountByGroup(Resources resources)
        {
            Dictionary<string, int> groupGroupCount = new Dictionary<string, int>();
            int total = 0;

            foreach (Resource res in resources)
            {
                total++;
                if (!groupGroupCount.ContainsKey(res.Group))
                {
                    groupGroupCount[res.Group] = 1;
                }
                else
                {
                    groupGroupCount[res.Group]++;
                }
            }

            groupGroupCount["Total"] = total;

            return groupGroupCount;
        }


        //Aggregate the Resources into a Location, rg based grouping.
        public static Dictionary<string, int> CountBySubscription(Resources resources)
        {
            Dictionary<string, int> subGroupCount = new Dictionary<string, int>();
            int total = 0;

            foreach (Resource res in resources)
            {
                total++;
                if (!subGroupCount.ContainsKey(res.Subscription))
                {
                    subGroupCount[res.Subscription] = 1;
                }
                else
                {
                    subGroupCount[res.Subscription]++;
                }
            }

            subGroupCount["Total"] = total;

            return subGroupCount;
        }
    }
}
